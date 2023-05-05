from datetime import date
from decimal import Decimal

from django.db import models

from accounts.models import Parent
from classes.models import Student


class Order(models.Model):
    class Meta:
        db_table = "orders"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    # meal_category = models.ForeignKey(MealCategory, default=1, on_delete=models.PROTECT)

    parent_id = models.ForeignKey(Parent, on_delete=models.RESTRICT, verbose_name="Идентификатор родителя")
    student_id = models.ForeignKey(Student, on_delete=models.RESTRICT, verbose_name="Идентификатор ученика")
    order_date = models.DateField(default=date.today)
    date_ordered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parent_id} : {self.student_id} {self.order_date} - (id: {self.id})"


class OrderItem(models.Model):
    class Meta:
        db_table = "order_items"
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

    order_id = models.ForeignKey(Order, on_delete=models.CASCADE,
                                 related_name="order_set")  # , related_name="order_set"
    meal_category = models.CharField(max_length=100, null=True, verbose_name="Название приёма пищи")
    product_name = models.CharField('Название товара', max_length=256, null=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} : {self.product_name} - {self.quantity} шт."

