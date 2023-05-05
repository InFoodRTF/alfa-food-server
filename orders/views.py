from rest_framework.response import Response
from rest_framework.views import APIView
from orders.models.order import OrderItem, Order

from classes.models import MealCategory

# Create your views here.
from classes.models import Grade


class MyOwnView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_staff and not hasattr(user, "canteenemployee"):
            return Response({"detail": "Permission denied."})

        result = {'meal_category': []}

        order_date = request.data.get('date')
        if order_date is None:  # TODO: Переделать, метод date_format_validate
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

                temp_dict[meal_category.category_name].append({grade.name: temp_dict_2})

                # students_order = Student.objects.filter(order__in=orders_meal_category)

                queryset = orders_meal_category

            result['meal_category'].append(temp_dict)

        return Response(result)

# class MenuView(RetrieveAPIView):
#     serializer_class = MenuParentSerializer
#
#     def get_object(self):
#         return self.request.user
#
#     def get_serializer(self, *args, **kwargs):
#         serializer_class = self.get_serializer_class()
#
#         user = self.request.user
#
#         if hasattr(user, 'parent'):
#             user = user.parent
#             serializer_class = MenuParentSerializer
#         else:
#             serializer_class = MenuParentSerializer
#
#         kwargs['context'] = self.get_serializer_context()
#
#         return serializer_class(user, **kwargs)
