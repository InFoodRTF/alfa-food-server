# Generated by Django 4.1.3 on 2023-03-25 15:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_menuitem_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='date_added',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
