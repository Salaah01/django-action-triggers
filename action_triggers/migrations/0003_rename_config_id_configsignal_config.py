# Generated by Django 4.2.15 on 2024-08-11 22:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "action_triggers",
            "0002_rename_models_config_content_types_config_active",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="configsignal",
            old_name="config_id",
            new_name="config",
        ),
    ]
