from django.db import models

# Create your models here.


class DateTimeFieldsModel(models.Model):
    """
        Абстрактная модель, определяющая 2 поля типа datetime.
        created - дата и время создания записи;
        updated - дата и время обновления записи.
    """

    created = models.DateTimeField(verbose_name='Добавлено', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Обновлено', auto_now=True)

    class Meta:
        abstract = True
