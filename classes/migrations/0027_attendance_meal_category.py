# Generated by Django 4.1.3 on 2022-12-25 07:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0026_remove_attendance_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='meal_category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='classes.mealcategory', verbose_name='Приём пищи'),
        ),
    ]
