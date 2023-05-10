from django.db import models

from classes.models.meal_features import MealTime

from accounts.models import Teacher


class ShiftChoice(models.IntegerChoices):
    FIRST = 1, "Первая"
    SECOND = 2, "Вторая"


class Grade(models.Model):
    class Meta:
        db_table = "grades"
        verbose_name = "Класс"
        verbose_name_plural = "Классы"

    name = models.CharField(max_length=6, unique=True, verbose_name="Класс")
    teacher = models.ForeignKey(Teacher, on_delete=models.RESTRICT, verbose_name="Учитель класса")
    shift = models.PositiveSmallIntegerField(
        choices=ShiftChoice.choices,
        default=ShiftChoice.FIRST,
        verbose_name="Смена обучения"
    )
    meal_time = models.ManyToManyField(MealTime, verbose_name="Время приёма пищи")

    def __str__(self):
        return f"{self.name} (ID: {self.id})"