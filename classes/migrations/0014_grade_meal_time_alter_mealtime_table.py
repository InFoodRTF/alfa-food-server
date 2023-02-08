# Generated by Django 4.1.3 on 2022-12-24 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0013_mealtime_grade_shift_alter_grade_grade_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='meal_time',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='classes.mealtime'),
        ),
        migrations.AlterModelTable(
            name='mealtime',
            table='meal_time',
        ),
    ]
