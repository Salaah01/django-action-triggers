# Generated by Django 4.2.15 on 2024-08-29 01:26

from django.db import migrations, models

import action_triggers.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('action_triggers', '0005_messagebrokerqueue_conn_details'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='content_types',
            field=models.ManyToManyField(help_text='Models to trigger actions on.', limit_choices_to=action_triggers.models.Config._content_type_limit_choices_to, related_name='configs', to='contenttypes.contenttype', verbose_name='Models'),
        ),
    ]
