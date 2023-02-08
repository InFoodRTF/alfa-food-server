from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Profile(models.Model):
    class Meta:
        db_table = "profiles"
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.user} profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Parent(models.Model):
    class Meta:
        db_table = "parents"
        verbose_name = "Родителя"
        verbose_name_plural = "Родителей"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user}"

    def get_full_name(self):
        return f"{self.user.last_name} {self.user.first_name} {self.user.profile.middle_name}".strip()


class Teacher(models.Model):
    class Meta:
        db_table = "teachers"
        verbose_name = "Учитель"
        verbose_name_plural = "Учители"

    user = models.OneToOneField(User,  on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}"


class CanteenEmployee(models.Model):
    class Meta:
        db_table = "canteen_empl"
        verbose_name = "Работник столовой"
        verbose_name_plural = "Работники столовой"

    user = models.OneToOneField(User,  on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}"


class Administrator(models.Model):
    class Meta:
        db_table = "admin"
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"

    user = models.OneToOneField(User,  on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}"
