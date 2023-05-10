from django.db import models


class MealCategory(models.Model):
    class Meta:
        db_table = "meal_category"
        verbose_name = "Приём пищи"
        verbose_name_plural = "Приёмы пищи"

    category_name = models.CharField(max_length=50, verbose_name="Название приёма пищи")

    def __str__(self):
        return f"{self.category_name} (ID: {self.id})"


class MealTime(models.Model):
    class Meta:
        db_table = "meal_time"
        verbose_name = verbose_name_plural = "Время приёма пищи"

    meal_category = models.ForeignKey(MealCategory, default=1, on_delete=models.CASCADE)
    meal_start = models.TimeField(auto_now=False, auto_now_add=False, verbose_name="Начало приёма пищи")
    meal_end = models.TimeField(auto_now=False, auto_now_add=False, verbose_name="Окончание приёма пищи")

    def __str__(self):
        return f"{self.meal_start} - {self.meal_end} (ID: {self.id})"