# Generated by Django 4.1.3 on 2023-03-23 21:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_menu_menu_items'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menu',
            name='menu_items',
        ),
    ]
