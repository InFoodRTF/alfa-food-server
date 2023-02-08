# Generated by Django 4.1.3 on 2022-12-25 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0021_remove_mealtime_meal_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='MealCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=50, verbose_name='Название приёма пищи')),
            ],
            options={
                'verbose_name': 'Приём пищи',
                'verbose_name_plural': 'Приёмы пищи',
                'db_table': 'meal_category',
            },
        ),
    ]
