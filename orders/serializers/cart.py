from rest_framework.serializers import ModelSerializer

from orders.models.cart import Cart, CartItem
from orders.models.menu import Menu
from orders.serializers.product import ProductSerializer


class CartItemSerializer(ModelSerializer):
    class Meta:
        model = CartItem
        exclude = ['cart', 'id']

    def to_representation(self, instance):
        rep = super(CartItemSerializer, self).to_representation(instance)
        menu_item = instance.menu_item
        product_serialized = ProductSerializer(menu_item.product).data
    #
    #     # Приведение к ответу для конкртеного типа юзеров
    #     # TODO: Требует изменения или доработки
    #     # if hasattr(self.context['request'].user, "parent"):
    #     #     [product_serialized.pop(item) for item in ['id', 'created', 'updated', 'description']]
    #     # rep.update(product=product_serialized)
        rep['product'] = product_serialized
        return rep


class CartSerializer(ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True, source="user_cart")

    class Meta:
        model = Cart
        exclude = ['id', ]  # 'active', 'date_added', 'date_implementation''

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

        rep['menu_date_implementation'] = Menu.objects.get(pk=rep['menu']).date_implementation.strftime("%d.%m.%Y")
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
