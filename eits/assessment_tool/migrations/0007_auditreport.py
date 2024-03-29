# Generated by Django 5.0.2 on 2024-03-19 17:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment_tool", "0006_archimateobject_company_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "report_file",
                    models.FileField(blank=True, null=True, upload_to="audit_reports/"),
                ),
                (
                    "audit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reports",
                        to="assessment_tool.audit",
                    ),
                ),
            ],
        ),
    ]
