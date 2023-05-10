from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from accounts.models import Parent
from classes.models.student import Student
from orders.models.menu import Menu, MenuItem


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
        MenuItem, through='CartItem', through_fields=('cart', 'menu_item'))

    def delete_all_cart_item(self):
        self.cart_items.through.objects.all().delete()  # Получаю все many_to_many objects (CartItem)
        # for item in self.cart_items.all():
        #     cart_item = CartItem.objects.get(cart=self, product=item)
        #     cart_item.delete()

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
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name='Продукт из меню')
    quantity = models.PositiveIntegerField('Количество', default=1,
                                           validators=[MaxValueValidator(10,
                                                                         'В корзину допустимо добавить только 10 единиц одного товара.'),
                                                       MinValueValidator(1, 'Значение не должно быть меньше единицы.')])

    def __str__(self) -> str:
        return f'В корзине покупателя {self.cart.customer} находится товар {self.menu_item} (x{self.quantity})'