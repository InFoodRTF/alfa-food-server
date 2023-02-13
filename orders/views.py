from datetime import date
from time import strptime

from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.viewsets import ModelViewSet

from accounts.models import Parent, CanteenEmployee
from classes.models import Student
from orders.models import Order, OrderItem, Product
from classes.models import MealCategory

from orders.permissons import IsOwnerOrStaff
from orders.serializers import OrderSerializer, OrderItemSerializer, ProductSerializer, OrderCanteenSerializer

from common.services import all_objects, filter_objects, create_objects
from orders.services import create_order_items

# Create your views here.
from classes.models import Grade


class MyOwnView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_staff and not hasattr(user, "canteenemployee"):
            return Response({"detail": "Permission denied."})

        result = {'meal_category': []}

        order_date = request.data.get('date')
        if order_date is None:
            return Response({"detail": "Date was not provided or incorrect data format, should be YYYY-MM-DD"})

        for meal_category in MealCategory.objects.all():

            temp_dict = {meal_category.category_name: []}

            grades = Grade.objects.all()

            for grade in grades:
                temp_dict_2 = {}
                temp_dict_2['shift'] = grade.shift
                temp_dict_2['order_items'] = []

                all_students = grade.student_set.all()

                orders_meal_category = Order.objects.filter(student_id__in=all_students,
                                                            order_date=order_date).filter(meal_category=meal_category)
                orders_item_in__orders = OrderItem.objects.filter(order__in=orders_meal_category)

                temp_dict_3 = {}
                for order_item in orders_item_in__orders:
                    temp_dict_3[order_item.product.name] = int(
                        temp_dict_3.get(order_item.product.name) or 0) + order_item.quantity

                for product, quantity in temp_dict_3.items():
                    temp_dict_2['order_items'].append({'product': product,
                                                       'quantity': quantity})

                temp_dict[meal_category.category_name].append({grade.grade: temp_dict_2})

                # students_order = Student.objects.filter(order__in=orders_meal_category)

                queryset = orders_meal_category

            result['meal_category'].append(temp_dict)

        return Response(result)


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


class ProductViewSet(ModelViewSet):
    queryset = all_objects(Product.objects)
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['price', 'meal_category']
    ordering_fields = ['price', ]
    # all_orders = Order.objects.all()
    # serializer = OrderSerializer(all_orders, many=True)

    @action(detail=True, methods=['GET'])  # TODO: Удалить/Изменить
    def info(self, request, pk=None):
        # return Response(self.get_queryset().values_list("id", flat=True))
        product = get_object_or_404(Product, pk=pk)
        return Response(product.description)

    @action(detail=True, methods=['GET'])  # TODO: Удалить/Изменить
    def with_info(self, request, pk=None):
        # return Response(self.get_queryset().values_list("id", flat=True))
        product = get_object_or_404(Product, pk=pk)
        # return Response(ProductSerializer.to_representation(ProductSerializer(product), product))
        return Response(ProductSerializer(product).data)