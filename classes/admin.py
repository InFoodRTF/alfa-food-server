from django.contrib import admin
from django.contrib.admin import ModelAdmin

from classes.models.attendance import Attendance, StudentAttendance
from classes.models.grade import Grade
from classes.models.meal_features import MealTime, MealCategory
from classes.models.student import Student


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

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(ModelAdmin):
    pass


@admin.register(MealTime)
class MealTimeAdmin(ModelAdmin):
    pass


@admin.register(MealCategory)
class MealCategoryAdmin(ModelAdmin):
    pass
