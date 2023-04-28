from datetime import datetime

from rest_framework.exceptions import ValidationError

from common.services import create_objects
from orders.models import OrderItem


def create_order_items(item):
    return create_objects(OrderItem.objects, **item)


def date_format_validate(date_text):
    try:
        validated_date = datetime.strptime(date_text, "%d.%m.%Y")
    except ValueError:
        raise ValidationError(detail=f"Значение '{date_text}' имеет неверный формат даты. Оно должно быть в "
                                     f"формате DD.MM.YYYY")
    return validated_date
