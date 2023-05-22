from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.models import Parent
from common.services import all_objects, date_format_validate
from orders.models.menu import Menu
from orders.serializers.menu import MenuSerializer


class MenuViewSet(ModelViewSet):
    queryset = all_objects(Menu.objects)
    # serializer_class = MenuSerializer

    def list(self, request, *args, **kwargs):  # Переопределил вывод GET ModelViewSet
        queryset = self.get_queryset()

        user = self.request.user
        if isinstance(user.parent, Parent):
            queryset = queryset.first()
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
        if isinstance(user.parent, Parent):

            menu_date = self.request.query_params.get('date')

            if menu_date is None:
                raise ValidationError(detail='Дата не была предоставлена')

            valid_menu_date = date_format_validate(menu_date)

            return Menu.objects.get_active_objects(date_implementation=valid_menu_date)
            # obj = Menu.objects.get(active=True)
            # return obj
        else:
            return all_objects(Menu.objects)
