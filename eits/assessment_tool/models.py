from django.core.files.base import ContentFile
from django.db import models
from django.template.loader import render_to_string

from . import assessments


class Control(models.Model):
    group_id = models.CharField(max_length=100)
    control_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.group_id


class Company(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Audit(models.Model):
    audit_date = models.DateField(auto_now=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='audits')

    def __str__(self):
        return self.company.name + ' Audit'


class CompanyAssessment(models.Model):
    ASSESSMENT_TYPES = (
        ('manual', 'Manual'),
        ('semi_automatic', 'Semi-Automatic'),
        ('automatic', 'Automatic'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='assessments')
    extra_fields = models.JSONField(null=True, blank=True)
    control = models.ForeignKey(Control, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    type = models.CharField(max_length=15, choices=ASSESSMENT_TYPES, default='manual')

    def save(self, *args, **kwargs):
        if not self.pk:
            cls = self.get_cls()
            if cls:
                if cls.type:
                    self.type = cls.type
        super().save(*args, **kwargs)

    def get_cls(self):
        cls_name = f"{str(self.control).replace('.', '')}Assessment"
        if hasattr(assessments, cls_name):
            cls = getattr(assessments, cls_name)
            return cls
        print(f"No assessment class found for: {self.control}")
        return None

    def get_instance(self):
        if hasattr(self, '_instance'):
            return self._instance
        cls = self.get_cls()
        if not cls:
            return None
        self._instance = cls(self, self.extra_fields)
        return self._instance

    def run_assessment(self, audit):
        instance = self.get_instance()
        try:
            instance.run()
        except Exception as e:
            AuditResult.objects.create(audit=audit, status=False, assessment=self, comments=str(e))
            print("Error occurred while running assessment")
            return
        results = instance.get_result_data()
        if instance.type == 'automatic':
            results.update({'reviewed': True})
        AuditResult.objects.create(audit=audit, assessment=self, **results)

    def create_manual_assessment_result(self, audit):
        AuditResult.objects.create(audit=audit, assessment=self, status=False)

    def __str__(self):
        return f"{self.company}-{self.control}"

    def get_help_text(self):
        cls_name = f"{self.control.group_id.replace('.', '')}Assessment"
        if hasattr(assessments, cls_name):
            cls = getattr(assessments, cls_name)
            return cls.help_text
        return ""


class AuditResult(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='results')
    status = models.BooleanField(help_text="True if the control passed, False if it failed")
    comments = models.TextField(null=True, blank=True)
    assessment = models.ForeignKey(CompanyAssessment, on_delete=models.CASCADE, related_name='audit_results')
    extra_fields = models.JSONField(null=True, blank=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.assessment.control}-{self.audit}"


class ArchimateObject(models.Model):
    type = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    object_id = models.CharField(max_length=300)
    properties = models.JSONField(null=True, blank=True)
    documentation = models.TextField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='archimate_objects')

    def __str__(self):
        return f"{self.type}-{self.name}"

    def get_related_objects(self):
        target_objects = ArchimateObject.objects.filter(
            source_relations__target=self
        )
        source_objects = ArchimateObject.objects.filter(
            target_relations__source=self
        )
        return (target_objects | source_objects).distinct()


class ArchimateRelationship(models.Model):
    type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=300)
    source = models.ForeignKey(ArchimateObject, on_delete=models.CASCADE, related_name='source_relations')
    target = models.ForeignKey(ArchimateObject, on_delete=models.CASCADE, related_name='target_relations')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='archimate_relationships')


class AuditReport(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    report_file = models.FileField(upload_to='audit_reports/', null=True, blank=True)

    def __str__(self):
        return f"Report for {self.audit} created at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def generate_report(self):
        audit_results = self.audit.results.all()
        passed_count = 0
        failed_count = 0
        reviewed_count = 0
        not_reviewed_count = 0

        for result in audit_results:
            if result.status:
                passed_count += 1
            else:
                failed_count += 1

            if result.reviewed:
                reviewed_count += 1
            else:
                not_reviewed_count += 1
        # Render the HTML report
        html_content = render_to_string('audit_report_template.html', {
            'audit': self.audit,
            'audit_results': audit_results,
            'passed_count': passed_count,
            'failed_count': failed_count,
            'reviewed_count': reviewed_count,
            'not_reviewed_count': not_reviewed_count,
        })

        # Save the rendered HTML to a file
        filename = f"audit_report_{self.audit.id}.html"
        self.report_file.save(filename, ContentFile(html_content.encode('utf-8')))
        self.save()
