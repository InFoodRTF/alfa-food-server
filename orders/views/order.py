from datetime import date

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.models import Parent
from classes.models import Student, MealCategory
from common.services import all_objects, create_objects
from orders.models.order import OrderItem, Order
from orders.permissons import IsOwnerOrStaff
from orders.serializers.order import OrderItemSerializer, OrderSerializer, OrderParentSerializer, OrderCanteenSerializer
from orders.services import create_order_items


# region Pagination

class OrderPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response(data, headers={'Orders-Total-Count': self.count})


# endregion

class OrderViewSet(ModelViewSet):
    def get_object(self):
        # queryset = self.get_queryset()

        obj = get_object_or_404(Order, pk=int(self.kwargs.get('pk')))
        # self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user

        if user.is_staff or hasattr(user, "canteenemployee"):
            queryset = Order.objects.all()
            order_date = self.request.query_params.get('date')
            if order_date is not None:
                queryset = queryset.filter(order_date=order_date)

                # for meal_category in MealCategory.objects.all():
                #     grades = Grade.objects.all()
                #     for grade in grades:
                #         all_students = grade.student_set.all()
                #
                #         orders_meal_category = Order.objects.filter(student_id__in=all_students,
                #                                                     order_date=order_date).filter(meal_category=meal_category)
                #         orders_item_in__orders = OrderItem.objects.filter(order__in=orders_meal_category)
                #
                #         # students_order = Student.objects.filter(order__in=orders_meal_category)
                #
                #         queryset = orders_meal_category
            return queryset

        if hasattr(user, "parent"):
            return Order.objects.filter(parent_id=user.parent.id)

    def get_serializer_class(self):
        if hasattr(self.request.user, "canteenemployee"):
            return OrderCanteenSerializer
        return OrderSerializer

    def canteen_order_view(self):
        pass

    # def get_serializer(self, *args, **kwargs):
    #     """
    #     Return the serializer instance that should be used for validating and
    #     deserializing input, and for serializing output.
    #     """
    #     if args is None or isinstance(args[0][0], Order):
    #         serializer_class = self.get_serializer_class()
    #     elif isinstance(args[0][0], OrderItem):
    #         serializer_class = OrderCanteenSerializer()
    #
    #
    #     kwargs.setdefault('context', self.get_serializer_context())
    #     return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        user = request.user

        try:
            if isinstance(user.parent, Parent):
                pass
        except:
            return Response({'detail': 'User must be Parent'}, status=status.HTTP_400_BAD_REQUEST)

        order_items = request.data.get('order_items')

        if order_items and len(order_items) == 0 or order_items is None:
            return Response({'detail': 'Order item was not provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Create order

        meal_category = MealCategory.objects.filter(id=int(request.data.get('meal_category')))

        if meal_category is None or len(meal_category) == 0:
            meal_category = MealCategory.objects.get(category_name="Завтрак")

        student_id = request.data.get("student_id")

        try:
            order_date = request.data.get("order_date")
        except:
            order_date = date.today

        order = create_objects(
            Order.objects,
            parent_id=user.parent,
            student_id=Student.objects.get(id=student_id),
            meal_category=meal_category.first(),
            order_date=order_date,
        )

        # Step 2: Add Order Items to Order
        # order_items = eval(order_items)
        try:
            if isinstance(order_items, list):
                for item in order_items:
                    item["order"] = order
                    create_order_items(item)

            # if isinstance(order_items, list):
            #     order_items["order"] = order
            #     create_order_items(order_items)
            # else:
            #     order_items = list(order_items)
            #
            #     for item in order_items:
            #         item["order"] = order
            #         create_order_items(item)
        except Exception as exc:
            print(exc)
            order.delete()
            return Response({'detail': 'The product ID was not provided or incorrectly request'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data)

    serializer_class = OrderSerializer
    pagination_class = OrderPagination

    permission_classes = [
        IsOwnerOrStaff,
    ]

    def get_serializer_class(self, *args, **kwargs):
        if hasattr(self.request.user, 'parent'):
            return OrderParentSerializer
        return OrderSerializer

    @action(detail=False, methods=['GET'])  # TODO: Удалить/Изменить
    def id(self, request):
        return Response(self.get_queryset().values_list("id", flat=True))

        # order = create_objects(Order.objects, user_id=user)
        # order_items = []
        # if "order_items" in request.data:
        #     for item in eval(request.data["order_items"]):
        #         item["order_id"] = order.id
        #         order_items.append(create_order_items(item))

        # for item in list(eval(request.data["order_items"])):
        #     item["order"] = order.id
        #     order_items.append(item)
        #
        # data = {"user_id": user.id, "order_items": order_items}
        # serializer = self.get_serializer(data=data)
        # serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderItemViewSet(ModelViewSet):
    queryset = all_objects(OrderItem.objects)
    serializer_class = OrderItemSerializer
