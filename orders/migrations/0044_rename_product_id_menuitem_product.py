# Generated by Django 4.1.3 on 2023-04-25 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0043_rename_products_cart_cart_items_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menuitem',
            old_name='product_id',
            new_name='product',
        ),
    ]
