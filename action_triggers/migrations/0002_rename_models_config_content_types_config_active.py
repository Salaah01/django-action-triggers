# Generated by Django 4.2.15 on 2024-08-11 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('action_triggers', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='config',
            old_name='models',
            new_name='content_types',
        ),
        migrations.AddField(
            model_name='config',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Active'),
        ),
    ]
