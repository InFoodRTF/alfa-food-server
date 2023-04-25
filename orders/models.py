import sys
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO

import django.utils.translation
from PIL import Image
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.
from django.core.files.storage import FileSystemStorage

from accounts.models import Parent
from alfafood.settings import STATIC_ROOT
from classes.models import Student, MealCategory
from common.services import all_objects
from django.utils.translation import gettext_lazy as _


# class ActiveObjectsManager(models.Manager):
#     def get_active_objects(self, date_implementation):
#         return self.filter(is_published=True, date_implementation=date_implementation)
#
#
# class SingleActiveObjectMixin(models.Model):
#     is_active = models.BooleanField(_("Выбрать текущим меню на сегодня"), default=False)
#     is_published = models.BooleanField(_("Опубликовать"), default=False)
#
#     objects = ActiveObjectsManager()
#
#     class Meta:
#         abstract = True
#         ordering = ['-is_active']
#
#     def save(self, *args, **kwargs):
#         if self.is_active and self.is_published:
#             try:
#                 currently_active = self.__class__.objects.get(is_active=True, date_implementation=self.date_implementation)
#             except self.__class__.DoesNotExist:
#                 pass
#             else:
#                 currently_active.is_active = False
#                 currently_active.save()
#         return super(SingleActiveObjectMixin, self).save(*args, **kwargs)
#
#     def get_state_string(self):
#         if self.is_active:
#             state = _("active")
#         else:
#             state = _("not active")
#         return state


class DateTimeFieldsModel(models.Model):
    """
        Абстрактная модель, определяющая 2 поля типа datetime.
        created - дата и время создания записи;
        updated - дата и время обновления записи.
    """

    created = models.DateTimeField(verbose_name='Добавлено', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Обновлено', auto_now=True)

    class Meta:
        abstract = True


class Product(DateTimeFieldsModel):
    """ Модель товара. """

    class Meta:
        db_table = "products"
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    name = models.CharField('Название товара', max_length=256, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    grams = models.IntegerField('Развесовка товара', null=True)
    description = models.CharField(max_length=500, null=True)

    meal_category = models.ForeignKey(MealCategory, default=1, on_delete=models.PROTECT)

    image = models.ImageField(upload_to="static/images/%d/%m/%Y", null=True, blank=True)

    def __str__(self):
        return f"{self.name} (ID:{self.id})"

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    # def save(self):
    #     # Opening the uploaded image
    #     im = Image.open(self.image)
    #
    #     output = BytesIO()
    #
    #     original_width, original_height = im.size
    #     # aspect_ratio = round(original_width / original_height)
    #     # desired_height = 100  # Edit to add your desired height in pixels
    #     # desired_width = desired_height * aspect_ratio
    #
    #     # Resize/modify the image
    #     im = im.resize((original_width, original_height))
    #
    #     # after modifications, save it to the output
    #     im.save(output, format='JPEG', quality=90)
    #     output.seek(0)
    #
    #     # change the imagefield value to be the newley modifed image value
    #     self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.image.name.split('.')[0], 'image/jpeg',
    #                                       sys.getsizeof(output), None)
    #
    #     super(Product, self).save()

    # def save(self):
    #     # if not self.id:
    #     #     self.image = self.compress_image(self.image)
    #
    #     #self.image = self.compress_image(self.image)
    #
    #     super(Product, self).save()

    # @staticmethod
    # def compress_image(image):
    #     img = Image.open(image).quantize(colors=256, method=Image.FASTOCTREE)#.convert("RGB")
    #     im_io = BytesIO()
    #
    #     if image.name.split('.')[1] == 'jpeg' or image.name.split('.')[1] == 'jpg':
    #         img.save(im_io, format='jpeg', optimize=True, quality=90)
    #         new_image = File(im_io, name="%s.jpeg" % image.name.split('.')[0], )
    #     else:
    #         img.save(im_io, format='png', optimize=True, quality=90)
    #         new_image = File(im_io, name="%s.png" % image.name.split('.')[0], )
    #
    #     return new_image


class MultipleActiveObjectsManager(models.Manager):
    def get_active_objects(self, date_implementation):
        return self.filter(active=True, date_implementation=date_implementation)


class ActiveObjectMixin(models.Model):
    active = models.BooleanField(
        verbose_name=_("Выбрать текущим меню на выбранную дату"),
        default=False,
        help_text=_("Нужно ли активировать данное меню?"),
    )
    objects = MultipleActiveObjectsManager()

    class Meta:
        abstract = True
        ordering = ("-active",)

    def save(self, *args, **kwargs):
        """
        If this object is active, deactivate all other active objects with the same
        date_implementation.
        """
        if self.active:
            try:
                currently_active = self.__class__.objects.get_active_objects(
                    self.date_implementation
                ).exclude(pk=self.pk)
            except self.__class__.DoesNotExist:
                pass
            else:
                currently_active.update(active=False)

        return super().save(*args, **kwargs)


class Menu(ActiveObjectMixin, DateTimeFieldsModel):
    class Meta:
        db_table = "menu"
        verbose_name = "Меню"
        verbose_name_plural = "Меню"

    date_implementation = models.DateField(default=date.today)
    # menu_items = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Меню на {self.date_implementation} : от {datetime.date(self.created)} - (id: {self.id})"


class MenuItem(models.Model):
    class Meta:
        db_table = "menu_items"
        verbose_name = "Элемент меню"
        verbose_name_plural = "Элементы меню"

    meal_category = models.ForeignKey(MealCategory, on_delete=models.PROTECT)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="menu_set")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} : {self.meal_category} - (Осталось: {self.quantity}) id: {self.id}"


class Cart(models.Model):
    """ Модель корзины. """

    class Meta:
        db_table = "cart"
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины покупателей'

    customer = models.OneToOneField(Parent, on_delete=models.CASCADE,
                                    verbose_name='Покупатель', related_name='cart_customer')

    # customer = models.ForeignKey(Parent, on_delete=models.CASCADE,
    #                              verbose_name='Покупатель', related_name='cart_customer')  # User -> Parent

    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True,
                                verbose_name='Ученик', related_name='cart_student')  # TODO: Это не работает. Исправить.

    # date = models.DateField(default=date.today, verbose_name='Дата')

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True,
                             verbose_name='Меню корзины', related_name='cart_menu')

    cart_items = models.ManyToManyField(
        MenuItem, through='CartItem', through_fields=('cart', 'product'))

    def __str__(self) -> str:
        return f'Корзина {self.customer.get_full_name()}'


class CartItem(models.Model):
    """
        Промужеточная модель между корзиной и товарами. Реализует дополнительное
        поле - количество конкретного товара в корзине.
    """

    class Meta:
        db_table = "cart_items"
        verbose_name = 'Продукт в корзине'
        verbose_name_plural = 'Продукты в корзине'

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name='Корзина', related_name='user_cart')
    product = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name='Продукт из меню')
    quantity = models.PositiveIntegerField('Количество', default=1,
                                           validators=[MaxValueValidator(10,
                                                                         'В корзину допустимо добавить только 10 единиц одного товара.'),
                                                       MinValueValidator(1, 'Значение не должно быть меньше единицы.')])

    def __str__(self) -> str:
        return f'В корзине покупателя {self.cart.customer} находится товар {self.product} (x{self.quantity})'


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



