from django.http import Http404
from rest_framework import viewsets, generics, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from classes.models.attendance import Attendance, StudentAttendance
from classes.models.grade import Grade
from classes.models.meal_features import MealCategory
from classes.models.student import Student
from classes.serializers.attendance import AttendanceSerializer, StudentAttendanceSerializer#, GradeAttendanceSerializer
from common.services import all_objects, filter_objects
from orders.models.order import Order


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint для просмотра, создания, изменения и удаления объектов Attendance
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return all_objects(Attendance.objects)

        if hasattr(user, "parent"):
            # TODO: Это сейчас не работает, просто ради заглушки
            ...

        if hasattr(user, "teacher"):
            teacher_grades = filter_objects(Grade.objects, teacher=user.teacher.id)
            return filter_objects(Attendance.objects, grade__in=teacher_grades)

    @action(detail=False, methods=['get'], url_path='grade/(?P<grade_pk>\d+)')
    def list_by_grade(self, request, grade_pk=None):
        """
        Список посещений для определенного студента
        """
        queryset = StudentAttendance.objects.filter(attendance__grade=grade_pk) #StudentAttendance.objects.filter(grade=grade_pk)
        if not queryset.exists():
            raise Http404
        serializer = StudentAttendanceSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='student/(?P<student_pk>\d+)')
    def list_by_student(self, request, student_pk=None):
        """
        Список посещений для определенного студента
        """
        queryset = StudentAttendance.objects.filter(student=student_pk)
        serializer = StudentAttendanceSerializer(queryset, many=True)
        return Response(serializer.data)




# class StudentAttendanceViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
#     """
#     ViewSet для посещаемости студента
#     """
#     queryset = Attendance.objects.all()
#     serializer_class = AttendanceSerializer
#
#     def perform_create(self, serializer):
#         # Получаем данные из запроса
#         student_id = self.kwargs['student_id']
#         meal_category_id = self.request.data.get('meal_category')
#         date = self.request.data.get('date')
#
#         # Получаем объекты из БД
#         student = Student.objects.get(pk=student_id)
#         meal_category = MealCategory.objects.get(pk=meal_category_id)
#
#         # Проверяем, был ли сделан заказ на эту дату
#         if not Order.objects.filter(student=student, meal_category=meal_category, date=date).exists():
#             raise ValidationError("Заказ на данную дату не найден")
#
#         # Добавляем данные об ученике и дате в сериализатор перед сохранением
#         serializer.save(student=student, date=date)
#
#     @action(detail=True, methods=['get'])
#     def list_by_student(self, request, pk=None):
#         """
#         Список посещений для определенного студента
#         """
#         queryset = self.queryset.filter(student=pk)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
#
#
# class ClassAttendanceViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
#     """
#     ViewSet для посещаемости класса
#     """
#     queryset = Attendance.objects.all()
#     serializer_class = AttendanceSerializer
#
#     def perform_create(self, serializer):
#         # Получаем данные из запроса
#         grade_id = self.kwargs['grade_id']
#         meal_category_id = self.request.data.get('meal_category')
#         date = self.request.data.get('date')
#
#         # Получаем объекты из БД
#         grade = Grade.objects.get(pk=grade_id)
#         meal_category = MealCategory.objects.get(pk=meal_category_id)
#
#         # Проверяем, был ли сделан заказ на эту дату
#         if not Order.objects.filter(grade=grade, meal_category=meal_category, date=date).exists():
#             raise ValidationError("Заказ на данную дату не найден")
#
#         # Добавляем данные о классе и дате в сериализатор перед сохранением
#         serializer.save(grade=grade, date=date)
#
#     @action(detail=True, methods=['get'])
#     def list_by_class(self, request, pk=None):
#         """
#         Список посещений для определенного класса
#         """
#         queryset = self.queryset.filter(grade=pk)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
