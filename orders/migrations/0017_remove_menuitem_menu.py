# Generated by Django 4.1.3 on 2023-03-23 21:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_alter_menuitem_menu'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menuitem',
            name='menu',
        ),
    ]
