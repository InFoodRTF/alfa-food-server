from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.models import Parent
from classes.models.meal_features import MealCategory
from common.permissions import IsCustomRole
from common.services import all_objects, date_format_validate
from orders.models.menu import Menu, MenuItem
from orders.models.product import Product
from orders.serializers.menu import MenuSerializer, MenuItemSerializer


class MenuViewSet(ModelViewSet):
    queryset = all_objects(Menu.objects)

    # serializer_class = MenuSerializer

    @permission_classes([IsCustomRole("canteenemployee")])
    @action(detail=False, methods=['post'], url_path="item/add")
    def add_menu_item(self, request, pk=None):
        menu_id = request.data.get("menu_id")  # self.get_object()
        product_id = request.data.get("product_id")
        meal_category_name = request.data.get("meal_category")

        if not menu_id:
            return Response({"error": "Menu ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        if not product_id:
            return Response({"error": "Product ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        if not meal_category_name:
            return Response({"error": "Meal Category Name not provided."}, status=status.HTTP_400_BAD_REQUEST)

        menu = Menu.objects.filter(pk=menu_id).first()
        meal_category = MealCategory.objects.filter(category_name=meal_category_name).first()
        product = Product.objects.filter(pk=product_id).first()
        if menu is None:
            return Response({"error": "The provided Menu ID does not exist."})
        if meal_category is None:
            return Response({"error": "The provided Meal Category Name does not exist."})
        if product is None:
            return Response({"error": "The provided Product ID does not exist."})

        # if cart.menu != menu_item.menu:
        #     return Response({"error": "The provided product is not in the menu"})

        menu_item, created = MenuItem.objects.get_or_create(menu=menu, product=product, meal_category=meal_category)

        if not created:
            menu_item.quantity += 1
            menu_item.save()

        serializer = MenuSerializer(menu)
        return Response(serializer.data)
        # menu_item_serializer = MenuItemSerializer(data=request.data)
        # menu_item_serializer.is_valid(raise_exception=True)
        # menu_item_serializer.save()
        # headers = self.get_success_headers(menu_item_serializer.data)
        # return Response(menu_item_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @permission_classes([IsCustomRole("canteenemployee")])
    @action(detail=False, methods=['post', 'delete'], url_path="item/remove")
    def remove_menu_item(self, request, pk=None):
        # menu_id = request.data.get("menu_id")

        menuitem_id = request.data.get("menuitem_id")

        # if not menu_id:
        #     return Response({"error": "Menu ID not provided."}, status=status.HTTP_400_BAD_REQUEST)
        if not menuitem_id:
            return Response({"error": "MenuItem ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        # menu = Menu.objects.filter(pk=menu_id).first()
        # if menu is None:
        #     return Response({"error": "The provided Menu ID does not exist."})

        try:
            menu_item = MenuItem.objects.get(pk=menuitem_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "MenuItem not found in menu."}, status=status.HTTP_404_NOT_FOUND)

        menu = menu_item.menu

        req_method = str(request.method).lower()

        if req_method == 'delete':
            menu_item.delete()
        elif req_method == 'post':
            if menu_item.quantity > 1:
                menu_item.quantity -= 1
                menu_item.save()
            else:
                menu_item.delete()

        serializer = MenuSerializer(menu)
        return Response(serializer.data)

    @permission_classes([IsCustomRole("canteenemployee")])
    @action(detail=False, methods=['get'], url_path="list")
    def get_all_menus_name_and_id(self, request, menu_date=None, pk=None):
        queryset = self.get_queryset()

        if menu_date is None:
            menu_date = request.query_params.get('date')

        if menu_date:
            if isinstance(menu_date, str):
                valid_menu_date = date_format_validate(menu_date).date()
            else:
                valid_menu_date = menu_date

            data = [{'id': item.id, 'name': item.get_name(),
                     'active': item.active if item.date_implementation == valid_menu_date else False,
                     'date_implementation': item.get_date()}
                    for item in queryset]
        else:
            data = [{'id': item.id, 'name': item.get_name(), 'date_implementation': item.get_date()}
                    for item in queryset]

        # data = [{'id': item.id, 'name': item.get_name()} for item in queryset]

        return Response(data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        active_param = request.data.get('active')#{'active': item.active if item.date_implementation == valid_menu_date.date() else False}

        menu_date_implementation = request.data.get('date')

        if not (active_param and menu_date_implementation):
            return Response({"error": "Active or Date not provided."})

        valid_menu_date_implementation = date_format_validate(menu_date_implementation).date()

        data = {'active': active_param, 'date_implementation': valid_menu_date_implementation}

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.get_all_menus_name_and_id(request=request, menu_date=valid_menu_date_implementation)

    def list(self, request, *args, **kwargs):  # Переопределил вывод GET ModelViewSet
        queryset = self.get_queryset()

        user = self.request.user
        if hasattr(user, 'parent'):
            if queryset.exists():
                queryset = queryset.first()
            else:
                raise Http404

            serializer = self.get_serializer(queryset)
        else:
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

        # if request.user.is_staff:
        #     queryset = self.get_queryset()
        #     serializer = self.get_serializer(queryset, many=True)
        #     return Response(serializer.data)
        #
        # try:
        #     instance = self.get_object()
        # except (Menu.DoesNotExist, KeyError):
        #     return Response({"error": "Requested Menu does not exist"}, status=status.HTTP_404_NOT_FOUND)
        #
        # serializer = self.get_serializer(instance)
        # return Response(serializer.data)

    def get_serializer_class(self, *args, **kwargs):
        # if hasattr(self.request.user, 'parent'):
        # return MenuParentSerializer
        return MenuSerializer

    def get_object(self):
        obj = get_object_or_404(Menu, pk=int(self.kwargs.get('pk')))
        return obj

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "parent"):

            menu_date = self.request.query_params.get('date')

            if menu_date is None:
                raise ValidationError(detail='Дата не была предоставлена')

            valid_menu_date = date_format_validate(menu_date)

            return Menu.objects.get_active_objects(date_implementation=valid_menu_date)
            # obj = Menu.objects.get(active=True)
            # return obj
        else:
            return all_objects(Menu.objects)


class MenuItemViewSet(ModelViewSet):
    queryset = all_objects(Menu.objects)

    serializer_class = MenuItemSerializer

    # def create(self, request, *args, **kwargs):
    #     self.super()