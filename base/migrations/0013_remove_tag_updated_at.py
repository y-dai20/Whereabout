# Generated by Django 3.2.5 on 2023-02-25 06:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20230225_1555'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='updated_at',
        ),
    ]
