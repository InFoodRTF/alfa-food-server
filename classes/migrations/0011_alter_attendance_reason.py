# Generated by Django 4.1.3 on 2022-12-22 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0010_alter_attendance_mark_attendance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='reason',
            field=models.TextField(blank=True, null=True, verbose_name='Причина отсутствия'),
        ),
    ]
