# Generated by Django 4.1.3 on 2023-04-10 13:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0031_alter_cart_table_alter_productincart_table'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menuitem',
            old_name='menu_id',
            new_name='menu',
        ),
    ]
