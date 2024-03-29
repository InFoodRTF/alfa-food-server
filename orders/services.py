from common.services import create_objects
from orders.models.order import OrderItem


def create_order_items(item):
    return create_objects(OrderItem.objects, **item)


