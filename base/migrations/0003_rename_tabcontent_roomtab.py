# Generated by Django 3.2.5 on 2023-02-16 14:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_tabcontent_room'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TabContent',
            new_name='RoomTab',
        ),
    ]
