# Generated by Django 4.1.3 on 2023-04-10 12:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0030_alter_cart_customer'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='cart',
            table='cart',
        ),
        migrations.AlterModelTable(
            name='productincart',
            table='product_in_cart',
        ),
    ]