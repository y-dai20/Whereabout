# Generated by Django 3.2.5 on 2023-02-16 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_rename_tabcontent_roomtab'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TabPermutation',
            new_name='RoomTabSequence',
        ),
    ]
