import xml.etree.ElementTree as ET

from django import forms
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.html import mark_safe

from . import assessments
from .models import Control, Audit, CompanyAssessment, Company, AuditResult, ArchimateObject, ArchimateRelationship


# Register your models here.

class GroupIdFilter(admin.SimpleListFilter):
    title = 'Group'  # or use 'verbose_name' of the field
    parameter_name = 'group_id'

    def lookups(self, request, model_admin):
        # This method returns a list of tuples. Each tuple is a pair (value, verbose value)
        # These values will be displayed in the admin's filter sidebar.
        group_ids = set([obj.group_id.split('.')[0] for obj in model_admin.model.objects.all()])
        return [(group_id, group_id) for group_id in group_ids]

    def queryset(self, request, queryset):
        # This method returns the filtered queryset based on the value
        # provided in the query string and retrievable via `self.value()`.
        if self.value():
            return queryset.filter(group_id__startswith=self.value())
        return queryset


@admin.register(Control)
class ControlAdmin(admin.ModelAdmin):
    fields = ('name', 'group_id', 'control_id', 'get_description_as_html')
    list_display = ('get_group_id_identification', 'name', 'group_id')
    search_fields = ('name', 'group_id', 'control_id', 'description')
    list_filter = (GroupIdFilter,)
    readonly_fields = ('get_description_as_html', 'control_id', 'group_id', 'name')

    def get_description_as_html(self, obj):
        return mark_safe(obj.description)

    get_description_as_html.short_description = 'Description'

    def get_group_id_identification(self, obj):
        return obj.group_id.split('.')[0] if obj.group_id else 'None'

    get_group_id_identification.short_description = 'Group'
    get_group_id_identification.admin_order_field = 'group_id'


class CompanyAssessmentForm(forms.ModelForm):
    class Meta:
        model = CompanyAssessment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CompanyAssessmentForm, self).__init__(*args, **kwargs)
        valid_controls = []
        for control in Control.objects.all():
            cls_name = f"{str(control).replace('.', '')}Assessment"
            if hasattr(assessments, cls_name):
                valid_controls.append(control.pk)

        self.fields['control'].queryset = Control.objects.filter(pk__in=valid_controls)


@admin.register(CompanyAssessment)
class CompanyAssessmentAdmin(admin.ModelAdmin):
    form = CompanyAssessmentForm
    fields = ('control', 'company', 'extra_fields', 'get_help_text', 'type')
    list_display = ('control', 'company')
    readonly_fields = ('get_help_text',)

    def get_help_text(self, obj):
        return obj.get_help_text()

    get_help_text.short_description = 'Extra fields help'


class XMLUploadForm(forms.Form):
    xml_file = forms.FileField()
    company = forms.ModelChoiceField(queryset=Company.objects)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ('name',)
    list_display = ('name',)
    actions = ['import_archimate_xml']

    change_list_template = 'admin/company.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-xml/', self.import_archimate_xml),
        ]
        return my_urls + urls

    def import_archimate_xml(self, request):
        if request.method == "POST":
            tree = ET.parse(request.FILES['xml_file'])
            company_id = request.POST.get('company')
            company = Company.objects.get(id=company_id)
            root = tree.getroot()
            relation_elements = []
            for element in root.findall('.//element'):
                if element.get('source') and element.get('target'):
                    relation_elements.append(element)
                else:
                    self.create_archi_object(element, company)
            for relation_element in relation_elements:
                self.create_archi_relationship(relation_element, company)
            self.message_user(request, "Your XML file has been imported")
            return redirect("..")
        form = XMLUploadForm()
        payload = {"form": form}
        return render(
            request, "admin/xml_upload.html", payload
        )

    def create_archi_object(self, element, company):
        name = element.get('name')
        obj_id = element.get('id')
        obj_type = element.get('{http://www.w3.org/2001/XMLSchema-instance}type')
        obj_type = obj_type.replace('archimate:', '')
        properties = {prop.get('key'): prop.get('value') for prop in element.findall('.//property')}
        documentation = element.find('.//documentation')
        if documentation is not None:
            documentation = documentation.text
        else:
            documentation = ''
        ArchimateObject.objects.update_or_create(
            object_id=obj_id,
            company=company,
            defaults={
                'type': obj_type,
                'name': name,
                'properties': properties if properties else {},
                'documentation': documentation
            }
        )

    def create_archi_relationship(self, element, company):
        source_id = element.get('source')
        target_id = element.get('target')
        obj_id = element.get('id')
        obj_type = element.get('{http://www.w3.org/2001/XMLSchema-instance}type')
        source = ArchimateObject.objects.get(object_id=source_id, company=company)
        target = ArchimateObject.objects.get(object_id=target_id, company=company)
        if not source or not target:
            return
        ArchimateRelationship.objects.update_or_create(
            object_id=obj_id,
            company=company,
            defaults={
                'type': obj_type,
                'source': source,
                'target': target
            }
        )


@admin.register(ArchimateObject)
class ArchimateObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'company')
    fields = ('type', 'name', 'company', 'documentation', 'properties', 'object_id')
    list_filter = ('company', 'type')
    search_fields = ('name', 'company', 'type', 'documentation', 'properties', 'object_id')


@admin.register(ArchimateRelationship)
class ArchimateRelationshipAdmin(admin.ModelAdmin):
    list_display = ('type', 'source', 'target', 'company')
    fields = ('type', 'source', 'target', 'company', 'object_id')
    list_filter = ('company', 'type', 'source', 'target')


class AuditResultInline(admin.TabularInline):
    model = AuditResult
    extra = 0  # Removes the extra empty forms
    readonly_fields = ('assessment', 'extra_fields')


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    fields = ('company',)
    list_display = ('audit_date', 'company',)
    inlines = [AuditResultInline]
    actions = ['start_audit']

    def start_audit(self, request, queryset):
        for audit in queryset:
            for assessment in audit.company.assessments.all():
                assessment.run_assessment(audit)


@admin.register(AuditResult)
class AuditResultAdmin(admin.ModelAdmin):
    fields = ('audit', 'status', 'reviewed', 'comments', 'extra_fields', 'assessment')
    list_display = ('audit', 'status', 'reviewed', 'assessment')
