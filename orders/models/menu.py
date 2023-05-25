from django.db import models

from datetime import date, datetime

from classes.models.meal_features import MealCategory
from common.models import DateTimeFieldsModel
from django.utils.translation import gettext_lazy as _

from orders.models.product import Product


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
    name = models.CharField(max_length=50, verbose_name="Название меню", null=True, blank=False, default=None)
    # menu_items = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True)

    def get_name(self):
        if self.name is None or len(self.name) <= 0:
            return f"Меню от {self.created.strftime('%d.%m.%Y %H:%M')}"
        else:
            return self.name

    def get_date(self):
        return self.date_implementation.strftime('%d.%m.%Y')

    def __str__(self):
        if self.name is None or len(self.name) <= 0:
            return f"Меню на {self.date_implementation} : от " \
                   f"{self.created.strftime('%d.%m.%Y %H:%M:%S')} - (id: {self.id})"

        return self.name


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