# Generated by Django 4.2 on 2023-05-24 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0045_rename_product_cartitem_menu_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='name',
            field=models.CharField(default=None, max_length=50, null=True, verbose_name='Название меню'),
        ),
    ]