from django.http import Http404
from rest_framework import viewsets, generics, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Teacher, Parent
from classes.models.attendance import Attendance, StudentAttendance, AttendanceChoice
from classes.models.grade import Grade
from classes.models.meal_features import MealCategory
from classes.models.student import Student
from classes.serializers.attendance import AttendanceSerializer, StudentAttendanceSerializer#, GradeAttendanceSerializer
from common.services import all_objects, filter_objects, date_format_validate, get_or_none
from orders.models.order import Order, OrderItem


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint для просмотра, создания, изменения и удаления объектов Attendance
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user

        queryset = self.get_queryset()

        if hasattr(user, 'parent'):
            ... # Заглушняк

        elif hasattr(user, 'teacher'):
            if request.query_params:
                attendance_grade_name = request.query_params.get('grade')
                attendance_meal_category_name = request.query_params.get('meal_category')
                attendance_date = request.query_params.get('date')
                if not (attendance_grade_name and attendance_meal_category_name and attendance_date):
                    return Response("Один или несколько параметров не были переданы", status=status.HTTP_400_BAD_REQUEST)

                attendance_grade = Grade.objects.get(name=attendance_grade_name)
                attendance_meal_category = MealCategory.objects.get(category_name=attendance_meal_category_name)
                validate_attendance_date = date_format_validate(attendance_date).date()

                students_attendance = []
                grade_students = attendance_grade.student_set.prefetch_related()
                for student in grade_students:
                    #  TODO: Сейчас это через OrderItem, переделай на Order. meal_category != category_name
                    if OrderItem.objects.filter(order_id__student_id=student,
                                                meal_category=attendance_meal_category.category_name,
                                                order_id__order_date=validate_attendance_date).exists():
                        students_attendance.append(student)

                attendance = get_or_none(Attendance,
                                         grade=attendance_grade,
                                         meal_category=attendance_meal_category,
                                         date=validate_attendance_date)

                if len(students_attendance) == 0 and attendance is None:
                    return Response("Отмечать нечего! Заказов на выбранные параметры ещё нет.",
                                    status=status.HTTP_404_NOT_FOUND)

                if attendance is None:
                    attendance, created = Attendance.objects.get_or_create(grade=attendance_grade,
                                                                           meal_category=attendance_meal_category,
                                                                           date=validate_attendance_date)
                for student in students_attendance:
                    StudentAttendance.objects.get_or_create(attendance=attendance, student=student,
                                                            mark_attendance=AttendanceChoice.PRESENT)

                serializer = self.get_serializer(attendance)
                return Response(serializer.data)

            else:
                return Response(self.get_serializer(self.get_queryset(), many=True).data)

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

    # @action(detail=False, methods=['GET'])
    # def list_by_query_params(self, request):
    #     # user = request.user
    #     # queryset_kwargs = dict()
    #
    #     if request.query_params:
    #         # student_id = request.query_params.get('id')
    #         # student_grade = request.query_params.get('grade')
    #         # attendance_date = request.query_params.get('date')
    #         # if student_id:
    #         #     queryset_kwargs.update(student=student_id)
    #         # if student_grade:
    #         #     queryset_kwargs.update(attendance__grade=student_grade)
    #         # if attendance_date:
    #         #     validate_attendance_date = date_format_validate(attendance_date)
    #         #     queryset_kwargs.update(attendance__date=validate_attendance_date)
    #
    #         attendance_grade_name = request.query_params.get('grade')
    #         attendance_meal_category_name = request.query_params.get('meal_category')
    #         attendance_date = request.query_params.get('date')
    #         if not (attendance_grade_name and attendance_meal_category_name and attendance_date):
    #             return Response("Один или несколько параметров не были переданы", status=status.HTTP_400_BAD_REQUEST)
    #
    #         attendance_grade = Grade.objects.get(name=attendance_grade_name)
    #         attendance_meal_category = MealCategory.objects.get(category_name=attendance_meal_category_name)
    #         validate_attendance_date = date_format_validate(attendance_date).date()
    #
    #         students_attendance = []
    #         grade_students = attendance_grade.student_set.prefetch_related()
    #         for student in grade_students:
    #             #  TODO: Сейчас это через OrderItem, переделай на Order. meal_category != category_name
    #             if OrderItem.objects.filter(order_id__student_id=student,
    #                                         meal_category=attendance_meal_category.category_name,
    #                                         order_id__order_date=validate_attendance_date).exists():
    #                 students_attendance.append(student)
    #
    #         attendance = get_or_none(Attendance,
    #                                  grade=attendance_grade,
    #                                  meal_category=attendance_meal_category,
    #                                  date=validate_attendance_date)
    #
    #         if len(students_attendance) == 0 and attendance is None:
    #             return Response("Отмечать нечего! Заказов на выбранные параметры ещё нет.",
    #                             status=status.HTTP_404_NOT_FOUND)
    #
    #         if attendance is None:
    #             attendance, created = Attendance.objects.get_or_create(grade=attendance_grade,
    #                                                                    meal_category=attendance_meal_category,
    #                                                                    date=validate_attendance_date)
    #         # attendance = Attendance.objects.get(grade=attendance_grade, meal_category=attendance_meal_category,
    #         #                                     date=validate_attendance_date)
    #
    #         # if created:
    #         # думал так сделать, но потом понял, что ученики могут дополнятся,
    #         # ибо учитель выберет дату раньше чем она наступила и всё трындец
    #         # grade_students = attendance_grade.student_set.prefetch_related()
    #         # for student in grade_students:
    #         #     #  TODO: Сейчас это через OrderItem, переделай на Order. meal_category != category_name
    #         #     if OrderItem.objects.filter(order_id__student_id=student,
    #         #                                 meal_category=attendance_meal_category.category_name,
    #         #                                 order_id__order_date=validate_attendance_date).exists():
    #         for student in students_attendance:
    #             StudentAttendance.objects.get_or_create(attendance=attendance, student=student,
    #                                                     mark_attendance=AttendanceChoice.PRESENT)
    #         # def perform_create(self, serializer):
    #         #         # Получаем данные из запроса
    #         #         student_id = self.kwargs['student_id']
    #         #         meal_category_name = self.request.data.get('meal_category')
    #         #         date = self.request.data.get('date')
    #         #
    #         #         # Получаем объекты из БД
    #         #         student = Student.objects.get(pk=student_id)
    #         #         meal_category = MealCategory.objects.get(category_name=meal_category_name)
    #         #
    #         #         # Проверяем, был ли сделан заказ на эту дату и выбранный приём пищи, посредством проверки OrderItem
    #         #         if not OrderItem.objects.filter(order_id__student_id=student, meal_category=meal_category,
    #         #                                         order_id__date_ordered=date).exists():
    #         #             raise ValidationError("Заказ на данную дату и категорию питания не найден")
    #         #
    #         #         # Добавляем данные об ученике и дате в сериализатор перед сохранением
    #         #         serializer.save(student=student, date=date)
    #
    #         serializer = self.get_serializer(attendance)
    #         return Response(serializer.data)
    #         # if attendance_grade:
    #         #     queryset_kwargs.update(student=attendance_grade)
    #         # if attendance_meal_category:
    #         #     queryset_kwargs.update(attendance__grade=attendance_meal_category)
    #         # if attendance_date:
    #         #     validate_attendance_date = date_format_validate(attendance_date)
    #         #     queryset_kwargs.update(attendance__date=validate_attendance_date)
    #
    #     else:
    #         return Response(self.get_serializer(self.get_queryset(), many=True).data)
    #

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


# class AttendanceViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint для просмотра, создания, изменения и удаления объектов Attendance
#     """
#     queryset = Attendance.objects.all()
#     serializer_class = AttendanceSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         user = self.request.user
#
#         if user.is_staff:
#             return all_objects(Attendance.objects)
#
#         if hasattr(user, "parent"):
#             # TODO: Это сейчас не работает, просто ради заглушки
#             ...
#
#         if hasattr(user, "teacher"):
#             teacher_grades = filter_objects(Grade.objects, teacher=user.teacher.id)
#             return filter_objects(Attendance.objects, grade__in=teacher_grades)
#
#     # @action(detail=False, methods=['get'], url_path='grade/(?P<grade_name>.+)')
#     # def list_by_grade(self, request, grade_name=None):
#     #     """
#     #     Список посещений всех студентов выбранного класса по дате
#     #     """
#     #     if not grade_name:
#     #         raise Http404
#     #     queryset_kwargs = dict()
#     #
#     #     grade = get_object_or_404(Grade, name=grade_name)
#     #     # queryset_kwargs.update(attendance__grade=grade)
#     #     queryset_kwargs.update(grade=grade)
#     #
#     #     # Проверка, передана ли дата посещаемости
#     #     attendance_date = self.request.query_params.get('date')
#     #     if attendance_date is not None:
#     #         valid_attendance_date = date_format_validate(attendance_date)
#     #         queryset_kwargs.update(date=valid_attendance_date)
#     #
#     #     # if attendance_date is None:
#     #     #     raise ValidationError(detail='Дата не была предоставлена')
#     #     queryset = Attendance.objects.filter(**queryset_kwargs)
#     #     # queryset = StudentAttendance.objects.filter(**queryset_kwargs)
#     #
#     #     # if grade_name:
#     #     #     queryset = StudentAttendance.objects.filter(attendance__grade_id=grade_pk)
#     #     # else:
#     #     #     grade_name = request.query_params.get('grade_name')
#     #
#     #     if not queryset.exists():
#     #         raise Http404
#     #
#     #     serializer = self.get_serializer(queryset, many=True)
#     #     # serializer = StudentAttendanceSerializer(queryset, many=True)
#     #     return Response(serializer.data)
#     #
#     # @action(detail=False, methods=['get'], url_path='student/(?P<student_pk>\d+)')
#     # def list_by_student(self, request, student_pk=None):
#     #     """
#     #     Список посещений для определенного студента
#     #     """
#     #     queryset = StudentAttendance.objects.filter(student=student_pk)
#     #     serializer = StudentAttendanceSerializer(queryset, many=True)
#     #     return Response(serializer.data)
#
#
class StudentAttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для посещаемости студента
    """
    queryset = StudentAttendance.objects.all()
    serializer_class = StudentAttendanceSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        mark_attendance = request.data.get('mark_attendance')

        if mark_attendance == 'true':
            instance.mark_attendance = AttendanceChoice.PRESENT
        elif mark_attendance == 'false':
            instance.mark_attendance = AttendanceChoice.ABSENT

        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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

    # def perform_create(self, serializer):
    #     # Получаем данные из запроса
    #     student_id = self.kwargs['student_id']
    #     meal_category_name = self.request.data.get('meal_category')
    #     date = self.request.data.get('date')
    #
    #     # Получаем объекты из БД
    #     student = Student.objects.get(pk=student_id)
    #     meal_category = MealCategory.objects.get(category_name=meal_category_name)
    #
    #     # Проверяем, был ли сделан заказ на эту дату и выбранный приём пищи, посредством проверки OrderItem
    #     if not OrderItem.objects.filter(order_id__student_id=student, meal_category=meal_category,
    #                                     order_id__date_ordered=date).exists():
    #         raise ValidationError("Заказ на данную дату и категорию питания не найден")
    #
    #     # Добавляем данные об ученике и дате в сериализатор перед сохранением
    #     serializer.save(student=student, date=date)

    # @action(detail=True, methods=['get'])
    # def list_by_student(self, request, pk=None):
    #     """
    #     Список посещений для определенного студента
    #     """
    #     queryset = self.queryset.filter(student=pk)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)
#
#
# class GradeAttendanceViewSet(viewsets.ModelViewSet):
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
#     def get_queryset(self):
#         return Attendance.objects.all()
#
#     def list(self, request, *args, **kwargs):  # Переопределил вывод GET ModelViewSet
#
#         user = request.user
#
#         if user.is_staff:
#             queryset = self.get_queryset()
#             serializer = self.get_serializer(queryset, many=True)
#
#         # try:
#         #     instance = self.get_object()
#         # except (Cart.DoesNotExist, KeyError):
#         #     return Response({"error": "Requested Cart does not exist"}, status=status.HTTP_404_NOT_FOUND)
#
#         queryset_kwargs = dict()
#
#         if isinstance(user.teacher, Teacher) and request.query_params:
#             grade_name = request.query_params.get('grade')
#             attendance_date = request.query_params.get('date')
#
#             if grade_name:
#                 grade = get_object_or_404(Grade, name=grade_name)
#                 queryset_kwargs.update(grade=grade)
#
#             if attendance_date:
#                 valid_attendance_date = date_format_validate(attendance_date)
#
#                 queryset_kwargs.update(date=valid_attendance_date)
#
#             attendances = Attendance.objects.filter(**queryset_kwargs)
#             if attendances is None:
#                 return ValidationError("Посещаемость не проставлена")
#
#             serializer = self.get_serializer(attendances, many=True)
#         else:
#             serializer = self.get_serializer(self.get_queryset(), many=True)
#
#         return Response(serializer.data)
#     # @action(detail=True, methods=['get'])
#     # def list_by_grade(self, request, pk=None):
#     #     """
#     #     Список посещений для определенного класса
#     #     """
#     #     queryset = self.queryset.filter(grade=pk)
#     #     serializer = self.get_serializer(queryset, many=True)
#     #     return Response(serializer.data)
