from django.http import Http404
from rest_framework import viewsets, generics, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Teacher
from classes.models.attendance import Attendance, StudentAttendance
from classes.models.grade import Grade
from classes.models.meal_features import MealCategory
from classes.models.student import Student
from classes.serializers.attendance import AttendanceSerializer, StudentAttendanceSerializer#, GradeAttendanceSerializer
from common.services import all_objects, filter_objects, date_format_validate
from orders.models.order import Order, OrderItem


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

    # @action(detail=False, methods=['get'], url_path='grade/(?P<grade_name>.+)')
    # def list_by_grade(self, request, grade_name=None):
    #     """
    #     Список посещений всех студентов выбранного класса по дате
    #     """
    #     if not grade_name:
    #         raise Http404
    #     queryset_kwargs = dict()
    #
    #     grade = get_object_or_404(Grade, name=grade_name)
    #     # queryset_kwargs.update(attendance__grade=grade)
    #     queryset_kwargs.update(grade=grade)
    #
    #     # Проверка, передана ли дата посещаемости
    #     attendance_date = self.request.query_params.get('date')
    #     if attendance_date is not None:
    #         valid_attendance_date = date_format_validate(attendance_date)
    #         queryset_kwargs.update(date=valid_attendance_date)
    #
    #     # if attendance_date is None:
    #     #     raise ValidationError(detail='Дата не была предоставлена')
    #     queryset = Attendance.objects.filter(**queryset_kwargs)
    #     # queryset = StudentAttendance.objects.filter(**queryset_kwargs)
    #
    #     # if grade_name:
    #     #     queryset = StudentAttendance.objects.filter(attendance__grade_id=grade_pk)
    #     # else:
    #     #     grade_name = request.query_params.get('grade_name')
    #
    #     if not queryset.exists():
    #         raise Http404
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     # serializer = StudentAttendanceSerializer(queryset, many=True)
    #     return Response(serializer.data)
    #
    # @action(detail=False, methods=['get'], url_path='student/(?P<student_pk>\d+)')
    # def list_by_student(self, request, student_pk=None):
    #     """
    #     Список посещений для определенного студента
    #     """
    #     queryset = StudentAttendance.objects.filter(student=student_pk)
    #     serializer = StudentAttendanceSerializer(queryset, many=True)
    #     return Response(serializer.data)


class StudentAttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для посещаемости студента
    """
    queryset = StudentAttendance.objects.all()
    serializer_class = StudentAttendanceSerializer

    def get_queryset(self):
        user = self.request.user
        queryset_kwargs = dict()

        if self.request.query_params:
            student_id = self.request.query_params.get('id')
            student_grade = self.request.query_params.get('grade')
            attendance_date = self.request.query_params.get('date')
            if student_id:
                queryset_kwargs.update(student=student_id)
            if student_grade:
                queryset_kwargs.update(attendance__grade=student_grade)
            if attendance_date:
                validate_attendance_date = date_format_validate(attendance_date)
                queryset_kwargs.update(attendance__date=validate_attendance_date)

        if user.is_staff:
            return StudentAttendance.objects.all()

        if hasattr(user, "parent"):
            # TODO: Это сейчас не работает, просто ради заглушки
            ...

        if hasattr(user, "teacher"):
            teacher_grades = filter_objects(Grade.objects, teacher=user.teacher.id)

            if len(queryset_kwargs) > 0:
                return StudentAttendance.objects.filter(**queryset_kwargs)

            return StudentAttendance.objects.filter(student__grade__in=teacher_grades)
            # return filter_objects(StudentAttendance.objects, =teacher_grades)

    def perform_create(self, serializer):
        # Получаем данные из запроса
        student_id = self.kwargs['student_id']
        meal_category_name = self.request.data.get('meal_category')
        date = self.request.data.get('date')

        # Получаем объекты из БД
        student = Student.objects.get(pk=student_id)
        meal_category = MealCategory.objects.get(category_name=meal_category_name)

        # Проверяем, был ли сделан заказ на эту дату и выбранный приём пищи, посредством проверки OrderItem
        if not OrderItem.objects.filter(order_id__student_id=student, meal_category=meal_category,
                                        order_id__date_ordered=date).exists():
            raise ValidationError("Заказ на данную дату и категорию питания не найден")

        # Добавляем данные об ученике и дате в сериализатор перед сохранением
        serializer.save(student=student, date=date)

    # @action(detail=True, methods=['get'])
    # def list_by_student(self, request, pk=None):
    #     """
    #     Список посещений для определенного студента
    #     """
    #     queryset = self.queryset.filter(student=pk)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


class GradeAttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для посещаемости класса
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def perform_create(self, serializer):
        # Получаем данные из запроса
        grade_id = self.kwargs['grade_id']
        meal_category_id = self.request.data.get('meal_category')
        date = self.request.data.get('date')

        # Получаем объекты из БД
        grade = Grade.objects.get(pk=grade_id)
        meal_category = MealCategory.objects.get(pk=meal_category_id)

        # Проверяем, был ли сделан заказ на эту дату
        if not Order.objects.filter(grade=grade, meal_category=meal_category, date=date).exists():
            raise ValidationError("Заказ на данную дату не найден")

        # Добавляем данные о классе и дате в сериализатор перед сохранением
        serializer.save(grade=grade, date=date)

    def get_queryset(self):
        return Attendance.objects.all()

    def list(self, request, *args, **kwargs):  # Переопределил вывод GET ModelViewSet

        user = request.user

        if user.is_staff:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

        # try:
        #     instance = self.get_object()
        # except (Cart.DoesNotExist, KeyError):
        #     return Response({"error": "Requested Cart does not exist"}, status=status.HTTP_404_NOT_FOUND)

        queryset_kwargs = dict()

        if isinstance(user.teacher, Teacher) and request.query_params:
            grade_name = request.query_params.get('grade')
            attendance_date = request.query_params.get('date')

            if grade_name:
                grade = get_object_or_404(Grade, name=grade_name)
                queryset_kwargs.update(grade=grade)

            if attendance_date:
                valid_attendance_date = date_format_validate(attendance_date)

                queryset_kwargs.update(date=valid_attendance_date)

            attendances = Attendance.objects.filter(**queryset_kwargs)
            if attendances is None:
                return ValidationError("Посещаемость не проставлена")

            serializer = self.get_serializer(attendances, many=True)
        else:
            serializer = self.get_serializer(self.get_queryset(), many=True)

        return Response(serializer.data)
    # @action(detail=True, methods=['get'])
    # def list_by_grade(self, request, pk=None):
    #     """
    #     Список посещений для определенного класса
    #     """
    #     queryset = self.queryset.filter(grade=pk)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)