from django.contrib.auth.models import User
from django.db.models import Manager


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
