from django.shortcuts import get_object_or_404
from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from common.services import all_objects
from orders.models.product import Product
from orders.serializers.product import ProductSerializer


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