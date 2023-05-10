from django.contrib import admin
from django.contrib.admin import ModelAdmin

from accounts.models import Profile, Parent, Teacher, CanteenEmployee, Administrator

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    pass


@admin.register(Parent)
class ParentAdmin(ModelAdmin):
    pass


@admin.register(Teacher)
class TeacherAdmin(ModelAdmin):
    pass


@admin.register(CanteenEmployee)
class CanteenEmployeeAdmin(ModelAdmin):
    pass


@admin.register(Administrator)
class AdministratorAdmin(ModelAdmin):
    pass
# class MyModelAdmin(admin.ModelAdmin):
#     def get_model_perms(self, request):
#         """
#         Return empty perms dict thus hiding the model from admin index.
#         """
#         return {}
#
# admin.site.unregister(AuthToken)
# admin.site.register(AuthToken, MyModelAdmin)

# admin.site.unregister(User)
#
#
# class UserProfileInline(admin.StackedInline):
#     model = Profile
#
#
# class UserProfileAdmin(UserAdmin):
#     inlines = [UserProfileInline, ]
#
#
# admin.site.register(User, UserProfileAdmin)
