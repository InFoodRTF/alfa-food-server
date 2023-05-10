from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from orders.models.menu import MenuItem, Menu
from orders.models.product import Product
from orders.serializers.product import ProductSerializer


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
        result = {} # TODO: Вывод категорий меню по порядку (Завтрак, Обед, Полдник, Ужин и только потом другие)
        # Либо придумай как по другому делать сортировку.

        for item in obj.menu_set.all():
            item_meal_category_name = item.meal_category.category_name

            item_serializer = MenuItemSerializer(item)

            result.setdefault(item_meal_category_name, list()).append(item_serializer.data)

        return result

    class Meta:
        model = Menu
        exclude = ['id', ]


# class MenuItemParentSerializer(ModelSerializer):
#     class Meta:
#         model = MenuItem
#         exclude = ['id', 'menu', ]
#
#     def to_representation(self, instance):
#         rep = super(MenuItemParentSerializer, self).to_representation(instance)
#         # TODO:Сделай продукт красивее
#         # rep['product_id'] = ProductSerializer().to_representation(Product.objects.get(pk=rep['product_id']))
#         return rep


# class MenuParentSerializer(ModelSerializer):
#     menu_items = MenuItemParentSerializer(many=True, source="menu_set")
#
#     class Meta:
#         model = Menu
#         exclude = ['id', ] # 'active', 'date_added', 'date_implementation'
#
#     def to_representation(self, instance):
#         rep = super(MenuParentSerializer, self).to_representation(instance)
#
#         # menu_items = [item for meal_category in MealCategory.objects.all() for item in
#         #               MenuItemParentSerializer.to_representation(MenuItem.objects.filter(meal_category=meal_category))]
#
#         return rep

    # def to_representation(self, instance):
    #     iterable = instance.all() if isinstance(instance, Manager) else instance
    #     return {
    #         meal_category: super().to_representation(Menu.objects.filter(meal_category=meal_category))
    #         for meal_category in MenuItem.objects.all()
    #     }