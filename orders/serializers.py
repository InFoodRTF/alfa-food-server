from collections import OrderedDict

from django.db.models import Manager
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from accounts.models import Parent
from classes.serializers import StudentSerializer, StudentParentSerializer
from orders.models import Order, OrderItem, Product, Menu, MenuItem, Cart, CartItem
from classes.models import MealCategory, Grade


class ProductOrderSerializer(ModelSerializer):
    class Meta:
        model = Product
        # fields = '__all__'
        exclude = ['id', 'description', 'meal_category']

    def to_representation(self, instance):
        rep = super(ProductOrderSerializer, self).to_representation(instance)
        return rep


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
        exclude = ['order_id', 'date_added']
        # fields = '__all__'#('id', 'product', 'quantity')

    def to_representation(self, instance):
        # TODO: переделать
        rep = super(OrderItemSerializer, self).to_representation(instance)
        # rep['product'] = Product.objects.get(id=rep['product']).name


        ###rep['product'] = ProductOrderSerializer().to_representation(Product.objects.get(id=rep['product']))
        ###rep.pop('product_id')


        # rep['meal_category'] = instance.meal_category.category_name
        # rep['student_id'] = StudentSerializer().to_representation(instance.student_id)
        return rep


class OrderParentSerializer(ModelSerializer):
    order_items = OrderItemSerializer(many=True, source="order_set")

    class Meta:
        model = Order
        # fields = '__all__'

        exclude = ['parent_id']

    def to_representation(self, instance):
        # TODO: переделать
        rep = super(OrderParentSerializer, self).to_representation(instance)

        # rep['meal_category'] = instance.meal_category.category_name
        rep['student'] = StudentParentSerializer().to_representation(instance.student_id)
        rep.pop('student_id')
        return rep


class OrderSerializer(ModelSerializer):
    # order_items = OrderItemSerializer(many=True, source="order_set")

    class Meta:
        model = Order
        fields = '__all__'

        # exclude = ['parent_id']

    def to_representation(self, instance):
        # TODO: переделать
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


class MenuItemSerializer(ModelSerializer):
    class Meta:
        model = MenuItem
        exclude = ['menu']

    def to_representation(self, instance):
        rep = super(MenuItemSerializer, self).to_representation(instance)
        # TODO:Сделай продукт красивее
        rep['product'] = ProductSerializer().to_representation(Product.objects.get(pk=rep['product']))
        return rep


class MenuSerializer(ModelSerializer):
    # menu_items = MenuItemSerializer(many=True, source="menu_set")

    items = SerializerMethodField()

    @staticmethod
    def get_items(obj):
        # result = {meal_category.category_name: [] for meal_category in MealCategory.objects.all()}
        result = {}

        for item in obj.menu_set.all():
            item_meal_category_name = item.meal_category.category_name

            item_serializer = MenuItemSerializer(item)

            result.setdefault(item_meal_category_name, list()).append(item_serializer.data)

        return result

    class Meta:
        model = Menu
        exclude = ['id', ]


class MenuItemParentSerializer(ModelSerializer):
    class Meta:
        model = MenuItem
        exclude = ['id', 'menu', ]

    def to_representation(self, instance):
        rep = super(MenuItemParentSerializer, self).to_representation(instance)
        # TODO:Сделай продукт красивее
        # rep['product_id'] = ProductSerializer().to_representation(Product.objects.get(pk=rep['product_id']))
        return rep


class MenuParentSerializer(ModelSerializer):
    menu_items = MenuItemParentSerializer(many=True, source="menu_set")

    class Meta:
        model = Menu
        exclude = ['id', ] # 'active', 'date_added', 'date_implementation'

    def to_representation(self, instance):
        rep = super(MenuParentSerializer, self).to_representation(instance)

        # menu_items = [item for meal_category in MealCategory.objects.all() for item in
        #               MenuItemParentSerializer.to_representation(MenuItem.objects.filter(meal_category=meal_category))]

        return rep

    # def to_representation(self, instance):
    #     iterable = instance.all() if isinstance(instance, Manager) else instance
    #     return {
    #         meal_category: super().to_representation(Menu.objects.filter(meal_category=meal_category))
    #         for meal_category in MenuItem.objects.all()
    #     }


class CartItemSerializer(ModelSerializer):
    class Meta:
        model = CartItem
        exclude = ['cart', 'id']

    def to_representation(self, instance):
        rep = super(CartItemSerializer, self).to_representation(instance)
        menu_item = MenuItem.objects.get(pk=rep['product'])
        product_serialized = ProductSerializer(menu_item.product).data

        # Приведение к ответу для конкртеного типа юзеров
        # TODO: Требует изменения или доработки
        # if hasattr(self.context['request'].user, "parent"):
        #     [product_serialized.pop(item) for item in ['id', 'created', 'updated', 'description']]
        rep.update(id=menu_item.id, product=product_serialized)
        return rep


class CartSerializer(ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True, source="user_cart")

    class Meta:
        model = Cart
        fields = '__all__'  # 'active', 'date_added', 'date_implementation''

    # def get_fields(self):
    #     ret = OrderedDict()
    #
    #     if not self.parent:
    #         print("No user associated with object")
    #         return ret
    #
    #     fields = super().get_fields()
    #
    #     # Bypass permission if superuser
    #     if self.user.is_superuser:
    #         return fields

        # for f in fields:
        #     if has_right(self.user, self.Meta.model.__name__.lower(), f, "read"):
        #         ret[f] = fields[f]

    #     return ret

    def to_representation(self, instance):
        rep = super(CartSerializer, self).to_representation(instance)

        # Приведение к ответу для конкртеного типа юзеров
        # TODO: изменить или дополнить
        # if hasattr(self.context['request'].user, "parent"):
        #     [rep.pop(item) for item in ['id', 'customer']]

        rep['menu_date_implementation'] = Menu.objects.get(pk=rep['menu']).date_implementation
        return rep

    # def to_representation(self, instance):
    #     rep = super(CartSerializer, self).to_representation(instance)
    #     # serializer = []
    #     # for prod in rep['products']:
    #     #     cart_item = CartItem.objects.get(pk=prod)
    #     #     serializer = CartItemSerializer(cart_item).data
    #     #     # res =
    #     products = [CartItemSerializer(CartItem.objects.get(pk=prod)).data for prod in rep['products']]
    #     rep.update(products=products)
    #     return rep