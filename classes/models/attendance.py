from django.db import models

from classes.models.student import Student

from classes.models.grade import Grade

from classes.models.meal_features import MealCategory
from datetime import date


class AttendanceChoice(models.IntegerChoices):
    PRESENT = 1, "Присутствовал"
    ABSENT = 2, "Отсутствовал"
    ABS_REASON = 3, "Отсутствовал по уважительной причине"


class Attendance(models.Model):
    class Meta:
        db_table = "attendance"
        verbose_name = "Посещаемость"
        verbose_name_plural = "Посещаемость"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Идентификатор ученика")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="Иденитификатор класса")
    meal_category = models.ForeignKey(MealCategory, on_delete=models.CASCADE, verbose_name="Приём пищи")
    # teacher = models.ForeignKey(Teacher, on_delete=models.RESTRICT, verbose_name="Идентификатор учителя")
    date = models.DateField(default=date.today, verbose_name="Дата посещения")
    mark_attendance = models.PositiveSmallIntegerField(
        choices=AttendanceChoice.choices,
        default=AttendanceChoice.PRESENT, verbose_name="Отметка посещаемости"
    )
    reason = models.TextField(verbose_name="Причина отсутствия", null=True, blank=True)

    def __str__(self):
        return f"{self.student.get_full_name()}: {AttendanceChoice(self.mark_attendance).label} (ID: {self.id})"