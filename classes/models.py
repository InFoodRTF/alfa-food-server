from django.contrib.auth.models import User
from accounts.models import Parent, Teacher
from django.db import models
from datetime import date, time


# Create your models here.

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


class Student(models.Model):
    class Meta:
        db_table = "students"
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
    # parent_id = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name="Идентификатор пользователя", )
    last_name = models.CharField(max_length=150, blank=False)
    first_name = models.CharField(max_length=150, blank=False)
    middle_name = models.CharField(max_length=150, blank=True)

    grade = models.ForeignKey(Grade, null=True, on_delete=models.RESTRICT, verbose_name="Класс ученика")
    #TODO Сделай выборку классов, типо не "7 Г", а чтоб было grade.nums/grade.letters

    parent_id = models.ForeignKey(Parent, on_delete=models.RESTRICT, verbose_name="Идентификатор родителя")
    # teacher_id = models.ForeignKey(Teacher, on_delete=models.RESTRICT, verbose_name="Идентификатор учителя")
    # date_ordered = models.DateTimeField(auto_now_add=True)

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    def __str__(self):
        return self.get_full_name() + f": {self.grade} // parent: {self.parent_id} - (id: {self.id})"


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
