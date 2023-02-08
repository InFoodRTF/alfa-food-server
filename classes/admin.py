from django.contrib import admin
from django.contrib.admin import ModelAdmin

from classes.models import Student, Grade, Attendance, MealTime, MealCategory


# Register your models here.

@admin.register(Student)
class StudentAdmin(ModelAdmin):
    pass


@admin.register(Grade)
class GradeAdmin(ModelAdmin):
    pass


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    pass


@admin.register(MealTime)
class MealTimeAdmin(ModelAdmin):
    pass


@admin.register(MealCategory)
class MealCategoryAdmin(ModelAdmin):
    pass
