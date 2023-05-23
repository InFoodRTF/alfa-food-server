from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Manager
from rest_framework.exceptions import ValidationError


def only_objects_decorator(func: callable):

    def only_objects_wrapper(objects, only=(), *args, **kwargs):
        return func(objects, *args, **kwargs).only(*only)

    return only_objects_wrapper


@only_objects_decorator
def all_objects(objects: Manager):
    return objects.all()


@only_objects_decorator
def filter_objects(objects: Manager, **kwargs):
    return objects.filter(**kwargs)


def create_objects(objects: Manager, **kwargs):
    return objects.create(**kwargs)


def date_format_validate(date_text):
    try:
        validated_date = datetime.strptime(date_text, "%d.%m.%Y")
    except ValueError:
        raise ValidationError(detail=f"Значение '{date_text}' имеет неверный формат даты. Оно должно быть в "
                                     f"формате DD.MM.YYYY")
    return validated_date


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None
