# Generated by Django 4.1.3 on 2022-12-20 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_order_date_product_meal_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateField(default='21-12-2022'),
        ),
    ]
