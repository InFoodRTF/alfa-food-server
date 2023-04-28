# Generated by Django 4.1.3 on 2023-04-23 22:47

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0038_alter_cart_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='product',
        ),
        migrations.RemoveField(
            model_name='order',
            name='meal_category',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='product_id',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product_menu',
            field=models.ForeignKey(default=8, on_delete=django.db.models.deletion.CASCADE, to='orders.menuitem', verbose_name='Продукт из меню'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='meal_category',
            field=models.CharField(max_length=100, null=True, verbose_name='Название приёма пищи'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_name',
            field=models.CharField(max_length=256, null=True, verbose_name='Название товара'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(through='orders.CartItem', to='orders.menuitem'),
        ),
    ]