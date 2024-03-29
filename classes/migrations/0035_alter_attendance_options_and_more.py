# Generated by Django 4.2 on 2023-05-14 21:05

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0034_remove_attendance_date_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendance',
            options={'verbose_name': 'Посещаемость класса', 'verbose_name_plural': 'Посещаемость класса'},
        ),
        migrations.RemoveField(
            model_name='studentattendance',
            name='grade_attendance',
        ),
        migrations.AddField(
            model_name='attendance',
            name='attended_students',
            field=models.ManyToManyField(through='classes.StudentAttendance', to='classes.student'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='date',
            field=models.DateField(default=datetime.date.today, verbose_name='Дата посещения'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='meal_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='classes.mealcategory', verbose_name='Приём пищи'),
        ),
        migrations.AddField(
            model_name='studentattendance',
            name='attendance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_attendances', to='classes.attendance'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classes.grade', verbose_name='Иденитификатор класса'),
        ),
        migrations.DeleteModel(
            name='GradeAttendance',
        ),
    ]
