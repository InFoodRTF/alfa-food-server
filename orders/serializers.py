from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from classes.serializers import StudentSerializer
from orders.models import Order, OrderItem, Product
from classes.models import MealCategory, Grade


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        # exclude = ['description']

    def to_representation(self, instance):
        rep = super(ProductSerializer, self).to_representation(instance)
        return rep


class OrderItemSerializer(ModelSerializer):
    # product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        exclude = ['id', 'order_id']
        # fields = '__all__'#('id', 'product', 'quantity')


class OrderSerializer(ModelSerializer):
    order_items = OrderItemSerializer(many=True, source="order_set")

    class Meta:
        model = Order
        # fields = '__all__'

        exclude = ['parent_id']

    def to_representation(self, instance):

        rep = super(OrderSerializer, self).to_representation(instance)
        # rep['meal_category'] = instance.meal_category.category_name
        # rep['student_id'] = StudentSerializer().to_representation(instance.student_id)
        return rep
    # def create(self, validated_data):
    #     return Order.objects.create(**validated_data)


class OrderCanteenSerializer(ModelSerializer):
    order_items = OrderItemSerializer(many=True, source="order_set")

    class Meta:
        model = Order
        fields = '__all__'

    def to_representation(self, instance):
        rep = super(OrderCanteenSerializer, self).to_representation(instance)
        rep['meal_category'] = instance.meal_category.category_name
        rep['student_id'] = StudentSerializer().to_representation(instance.student_id)
        return rep

    # def to_representation(self, instance):
    #     result = {}
    #     # meal_categories =
    #     # rep = super(OrderCanteenSerializer, self).to_representation(instance)
    #     return Response({
    #         "MealCaregory": MealCategory(self, context=self.get_serializer_context()).data,
    #         # "token": AuthToken.objects.create(user)[1]
    #     })
    #     return rep

    # product = ProductSerializer(read_only=True)
    #
    # class Meta:
    #     model = OrderItem
    #     fields = '__all__'  # ('id', 'product', 'quantity')
    #
    # def to_representation(self, instance):
    #
    #     rep = super(OrderItemSerializer, self).to_representation(instance)
    #     rep['meal_category'] = instance.meal_category.category_name
    #     rep['student_id'] = StudentSerializer().to_representation(instance.student_id)