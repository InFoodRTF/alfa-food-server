# Generated by Django 4.2 on 2023-05-02 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0044_rename_product_id_menuitem_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='product',
            new_name='menu_item',
        ),
    ]