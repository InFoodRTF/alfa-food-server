from django.shortcuts import get_object_or_404
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from common.constants import ADMIN_ROLE
from common.services import all_objects
from orders.models.product import Product
from orders.serializers.product import ProductSerializer

import logging

logger = logging.getLogger(__name__)


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

    def create(self, request, **kwargs): # TODO: переделать, это просто пример
        role = request.user.role
        if role == ADMIN_ROLE:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info("Admin user created new product: %s", serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error("Admin user failed to create new product: %s", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.warning("Unauthorized user tried to create new product: %s", request.user)
            return Response("Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
