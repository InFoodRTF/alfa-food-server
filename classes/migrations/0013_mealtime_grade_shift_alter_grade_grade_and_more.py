# Generated by Django 4.1.3 on 2022-12-24 16:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_canteenemployee'),
        ('classes', '0012_alter_grade_grade'),
    ]

    operations = [
        migrations.CreateModel(
            name='MealTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal_start', models.TimeField()),
                ('meal_end', models.TimeField()),
            ],
            options={
                'verbose_name': 'Время приёма пищи',
                'verbose_name_plural': 'Время приёма пищи',
                'db_table': 'mealTime',
            },
        ),
        migrations.AddField(
            model_name='grade',
            name='shift',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Первая'), (2, 'Вторая')], default=1, verbose_name='Смена обучения'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='grade',
            field=models.CharField(max_length=6, unique=True, verbose_name='Класс'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='teacher',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.RESTRICT, to='accounts.teacher', verbose_name='Учитель класса'),
        ),
    ]