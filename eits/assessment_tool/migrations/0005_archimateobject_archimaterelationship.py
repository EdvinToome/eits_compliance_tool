# Generated by Django 5.0.2 on 2024-03-16 18:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment_tool", "0004_auditresult_reviewed"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArchimateObject",
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
                ("type", models.CharField(max_length=100)),
                ("name", models.CharField(max_length=200)),
                ("object_id", models.CharField(max_length=300)),
                ("properties", models.JSONField(blank=True, null=True)),
                ("documentation", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="ArchimateRelationship",
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
                ("type", models.CharField(max_length=100)),
                ("object_id", models.CharField(max_length=300)),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="source_relations",
                        to="assessment_tool.archimateobject",
                    ),
                ),
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="target_relations",
                        to="assessment_tool.archimateobject",
                    ),
                ),
            ],
        ),
    ]
