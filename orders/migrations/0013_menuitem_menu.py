# Generated by Django 4.1.3 on 2023-03-23 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0031_alter_grade_teacher'),
        ('orders', '0012_rename_order_orderitem_order_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(blank=True, default=1, null=True)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.product')),
            ],
            options={
                'verbose_name': 'Элемент меню',
                'verbose_name_plural': 'Элементы меню',
                'db_table': 'menu_items',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('meal_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='classes.mealcategory')),
                ('menu_items', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.menuitem')),
            ],
            options={
                'verbose_name': 'Меню',
                'verbose_name_plural': 'Меню',
                'db_table': 'menu',
            },
        ),
    ]
