from datetime import date

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.core.files.storage import FileSystemStorage

from accounts.models import Parent
from alfafood.settings import STATIC_ROOT
from classes.models import Student, MealCategory
from common.services import all_objects


class Product(models.Model):
    class Meta:
        db_table = "products"
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    grams = models.IntegerField(null=True)
    description = models.CharField(max_length=500, null=True)

    meal_category = models.ForeignKey(MealCategory, default=1, on_delete=models.PROTECT)

    image = models.ImageField(upload_to="static/images", null=True, blank=True)

    def __str__(self):
        return f"{self.name} (ID:{self.id})"

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    class Meta:
        db_table = "orders"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    meal_category = models.ForeignKey(MealCategory, default=1, on_delete=models.PROTECT)

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

    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_set")  # , related_name="order_set"
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order} : {self.product} - {self.quantity} шт."

