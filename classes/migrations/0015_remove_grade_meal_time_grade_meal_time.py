# Generated by Django 4.1.3 on 2022-12-24 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0014_grade_meal_time_alter_mealtime_table'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grade',
            name='meal_time',
        ),
        migrations.AddField(
            model_name='grade',
            name='meal_time',
            field=models.ManyToManyField(default=1, to='classes.mealtime'),
        ),
    ]