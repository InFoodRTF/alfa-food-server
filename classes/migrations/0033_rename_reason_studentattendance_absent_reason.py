# Generated by Django 4.2 on 2023-05-10 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0032_remove_attendance_mark_attendance_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studentattendance',
            old_name='reason',
            new_name='absent_reason',
        ),
    ]
