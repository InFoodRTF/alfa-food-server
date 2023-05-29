from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.viewsets import ModelViewSet

from accounts.models import Parent
from classes.models.student import Student
from common.services import all_objects, filter_objects, date_format_validate
from orders.models.cart import CartItem, Cart
from orders.models.menu import MenuItem, Menu
from orders.models.order import OrderItem
from orders.serializers.cart import CartSerializer
from orders.serializers.order import OrderSerializer, OrderParentSerializer


class CartViewSet(ModelViewSet):
    queryset = all_objects(Cart.objects)
    serializer_class = CartSerializer

    def list(self, request, *args, **kwargs):  # Переопределил вывод GET ModelViewSet

        user = request.user

        if user.is_staff:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

        # try:
        #     instance = self.get_object()
        # except (Cart.DoesNotExist, KeyError):
        #     return Response({"error": "Requested Cart does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(user, 'parent'):
            instance = self.get_object()

            if request.query_params:
                menu_date = request.query_params.get('menu_date')
                student_id = request.query_params.get('student_id')

                if menu_date:
                    valid_menu_date = date_format_validate(menu_date)

                    if valid_menu_date.date() < datetime.today().date():
                        return Response({'detail': f"Выбранная дата '{valid_menu_date}' предшествует текущей"},
                                        status=status.HTTP_400_BAD_REQUEST)

                    menu = get_object_or_404(Menu, date_implementation=valid_menu_date, active=True)

                    if instance.menu != menu:
                        instance.delete_all_cart_item()
                        instance.menu = menu
                        instance.save()

                if student_id:
                    student = get_object_or_404(Student, pk=int(student_id), parent_id=user.parent)

                    if instance.student != student:
                        instance.delete_all_cart_item()
                        instance.student = student
                        instance.save()

            # Проверка на то, что корзина точно будет иметь корректное меню. Иначе -- None.
            instance_menu_date = instance.menu.date_implementation
            if instance_menu_date < datetime.today().date():

                future_menu = Menu.objects.filter(date_implementation__gte=instance_menu_date, active=True) \
                    .order_by('date_implementation').first()

                if future_menu is not None:
                    instance.menu = future_menu
                else:
                    instance.menu = None

                instance.save()
            # Сериализуем полностью прошедший проверку instance (cart)
            serializer = self.get_serializer(instance)
        else:
            serializer = self.get_serializer(self.get_queryset(), many=True)

        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return all_objects(Cart.objects)

        if hasattr(user, "parent"):
            return filter_objects(Cart.objects, customer=user.parent)  # Возвращает список с 1 элементом

    def get_object(self):
        user = self.request.user
        if hasattr(user, "parent"):
            obj, created = Cart.objects.get_or_create(customer=user.parent)
            return obj
        return ValueError(f'Cannot query "{user.name}": Must be "Parent" instance')

    @action(detail=False, methods=['post'])
    def add(self, request, pk=None):
        cart = self.get_object()
        menuitem_id = request.data.get("menuitem_id")

        if not menuitem_id:
            return Response({"error": "Item ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        menu_item = MenuItem.objects.filter(pk=menuitem_id).first()
        if menu_item is None:
            return Response({"error": "The provided menu_item ID does not exist."})

        if cart.menu != menu_item.menu:
            return Response({"error": "The provided menu_item is not in the menu"})

        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post', 'delete'])
    def remove(self, request, pk=None):
        cart = self.get_object()
        menuitem_id = request.data.get("menuitem_id")

        if not menuitem_id:
            return Response({"error": "Item ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(cart=cart, menu_item=menuitem_id)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND)

        req_method = str(request.method).lower()

        if req_method == 'delete':
            cart_item.delete()
        elif req_method == 'post':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def reset(self, request, pk=None):
        '''Сбрасывает состояние корзины, кроме выбранного ребёнка'''
        cart = self.get_object()

        cart.delete_all_cart_item()

        target_date = cart.menu.date_implementation

        future_menu = Menu.objects.filter(date_implementation__gte=target_date, active=True)\
            .order_by('date_implementation').first()

        if future_menu is not None:
            cart.menu = future_menu
            cart.save()
        else:
            Response({'detail': 'Корзина была очищена, но сейчас нет активных меню.'})

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='create-order')
    def create_order(self, request, pk=None):
        user = self.request.user
        if hasattr(user, "parent"):
            cart = self.get_object()
            parent = cart.customer

            if user.parent != parent:
                return Response({'error': 'Владелец корзины и пользователь отличаются.'})

            student = cart.student
            order_date = cart.menu.date_implementation

            if order_date < datetime.today().date():
                return Response({'detail': 'Невозможно оформить заказ. Выбранная дата предшествует текущей'},
                                status=status.HTTP_400_BAD_REQUEST)

            # order_date = request.data.get("order_date")
            order_data = {
                'parent_id': parent.id,
                'student_id': student.id,
                'order_date': order_date
            }
            order_serializer = OrderSerializer(data=order_data)
            order_serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                order = order_serializer.save()
                cart_items = CartItem.objects.filter(cart=cart)
                for cart_item in cart_items:

                    # menu_item = MenuItem.objects.get(pk=cart_item.product) # TODO:Сделать сообщение о том, что закончился товар
                    menu_item = cart_item.product

                    if menu_item.quantity > 1:
                        menu_item.quantity -= cart_item.quantity # TODO: сейчас вообще может уйти в минус
                        menu_item.save()
                    else:
                        continue

                    order_item = OrderItem(
                        order_id=order,
                        product_name=cart_item.product.product.name,
                        meal_category=cart_item.product.product.meal_category,
                        price=cart_item.product.product.price,
                        quantity=cart_item.quantity,
                    )
                    order_item.save()

                cart_items.delete()
            order_serializer = OrderParentSerializer(order)
            cart_serializer = CartSerializer(cart)
            return Response(
                {'order': order_serializer.data, 'cart': cart_serializer.data},
                status=status.HTTP_200_OK
            )