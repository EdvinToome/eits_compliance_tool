from django.contrib import admin
from django.utils.html import mark_safe

from .models import Control, Audit, CompanyAssessment, Company, AuditResult


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


@admin.register(CompanyAssessment)
class CompanyAssessmentAdmin(admin.ModelAdmin):
    fields = ('control', 'company', 'extra_fields', 'get_help_text', 'type')
    list_display = ('control', 'company')
    readonly_fields = ('get_help_text',)

    def get_help_text(self, obj):
        return obj.get_help_text()

    get_help_text.short_description = 'Extra fields help'


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ('name',)
    list_display = ('name',)


class AuditResultInline(admin.TabularInline):
    model = AuditResult
    extra = 0  # Removes the extra empty forms
    readonly_fields = ( 'assessment', 'extra_fields')


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    fields = ('company',)
    list_display = ('audit_date', 'company',)
    inlines = [AuditResultInline]
    actions = ['start_audit']

    def start_audit(self, request, queryset):
        for audit in queryset:
            for assessment in audit.company.assessments.filter(type__in=['semi_automatic', 'automatic']):
                assessment.run_assessment(audit)
            for assessment in audit.company.assessments.filter(type='manual'):
                assessment.create_manual_assessment_result(audit)



@admin.register(AuditResult)
class AuditResultAdmin(admin.ModelAdmin):
    fields = ('audit', 'status', 'comments', 'extra_fields', 'assessment')
    list_display = ('audit', 'status', 'assessment')
