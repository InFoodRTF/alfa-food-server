import datetime
from datetime import date

from django.http import Http404
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.models import Parent, Teacher
from classes.models import Student, Attendance, Grade, AttendanceChoice, MealCategory
from classes.serializers import StudentSerializer, AttendanceSerializer, GradeSerializer, StudentParentSerializer, \
    GradeParentSerializer
from common.services import all_objects, filter_objects, create_objects
from orders.models import Order


# Create your views here.

class StudentViewSet(ModelViewSet):
    def get_queryset(self):
        """
        This view should return a list of all students
        for the currently authenticated user.
        """
        user = self.request.user

        if user.is_staff:
            return all_objects(Student.objects)

        if hasattr(user, "parent"):
            return filter_objects(Student.objects, parent_id=user.parent.id)

        if hasattr(user, "teacher"):
            teacher_grades = filter_objects(Grade.objects, teacher=user.teacher.id)
            return filter_objects(Student.objects, grade__in=teacher_grades)

    # serializer_class = StudentSerializer

    permission_classes = (IsAuthenticated, )

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['grade']

    def get_serializer_class(self, *args, **kwargs):
        if hasattr(self.request.user, 'parent'):
            return StudentParentSerializer
        return StudentSerializer


class AttendanceViewSet(ModelViewSet):

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['grade', 'date', '']

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        mark_attendance = request.data.get('mark_attendance')
        if mark_attendance is not None:
            kwargs['mark_attendance'] = mark_attendance
        else:
            return Response({'detail': 'Разрешено изменять только поле mark_attendance'},
                            status=status.HTTP_400_BAD_REQUEST)
        return self.update(request, *args, **kwargs)

    # def perform_update(self, serializer):
    #     attendance_instance = serializer.instance
    #     request = self.request
    #     mark_attendance = request.data.get('mark_attendance')
    #
    #     if mark_attendance is None:
    #         return Response({'detail': 'Wrong parameters'}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     serializer.save(mark_attendance=mark_attendance)
    #     return Response(status=status.HTTP_200_OK)

    # def patch(self, request, pk):
    #     testmodel_object = self.get_object(pk)
    #     serializer = AttendanceSerializer(testmodel_object, data=request.data,
    #                                      partial=True)  # set partial=True to update a data partially
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response({'detail': 'wrong parameters'}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user

        if self.action == "partial_update":
            return Attendance.objects.all()

        data_grade_id = self.request.query_params.get('grade')

        if data_grade_id is None:
            raise ValidationError({'detail': 'Grade was not provided'})

        grade = Grade.objects.get(name=data_grade_id)  #

        try:
            attendance_date = self.request.query_params.get['date']
            datetime.datetime.strptime(attendance_date, '%Y-%m-%d')
        except:
            raise ValidationError({'detail': "Date was not provided or incorrect data format, should be YYYY-MM-DD"})

        meal_category = self.request.query_params.get('meal_category')

        if meal_category is None:
            raise ValidationError({'detail': 'Meal category was not provided'})
        # try:
        #     meal_category = self.request.data['meal_category']
        #
        #     grade.meal_time.get(meal_category=meal_category)
        # except:
        #     return Response({'detail': 'Meal category was not provided'}, status=status.HTTP_400_BAD_REQUEST)

        all_students = grade.student_set.all()

        orders_meal_category = Order.objects.filter(student_id__in=all_students,
                                                    order_date=attendance_date).filter(meal_category=meal_category)
        students_order = Student.objects.filter(order__in=orders_meal_category)
        #Student.objects.filter(orderset=orders_meal_category).values() Student.objects.filter(order__in=orders_meal_category)

        for student in students_order:
            if not Attendance.objects.filter(student=student.id, date=attendance_date, meal_category=meal_category):
                Attendance.objects.create(student=student,
                                          grade=grade,
                                          meal_category=MealCategory.objects.get(id=meal_category),
                                          date=attendance_date,
                                          mark_attendance=1,
                                          reason="")

        if user.is_staff or hasattr(user, "canteenemployee"):
            return all_objects(Attendance.objects)

        if hasattr(user, "teacher"):
            return Attendance.objects.filter(student_id__in=students_order,
                                             date=attendance_date, meal_category=meal_category)

    def create(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = AttendanceSerializer(queryset, many=True)
        data = serializer.data
        return Response({'attendance': data},
                        status=status.HTTP_200_OK)  # Переделать
        # user = request.user
        #
        # try:
        #     if isinstance(user.teacher, Teacher):
        #        pass
        # except:
        #     return Response({'detail': 'User must be Teacher'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # student = request.data.get('student')
        #
        # if student and len(student) == 0 or student is None:
        #     return Response({'detail': 'Student item was not provided'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # mark_attendance = request.data.get('mark_attendance')
        # if mark_attendance is None or int(mark_attendance) not in [member.value for member in AttendanceChoice]:
        #     mark_attendance = AttendanceChoice.PRESENT
        #
        #
        # # Step 1: Create attendance
        #
        # date_attendance = request.data.get("date")
        # if date_attendance is None:
        #     date_attendance = date.today()
        #
        #
        # reason = request.data.get('reason')
        # if reason is None:
        #     reason = ""
        #
        # student = Student.objects.get(id=student)
        # attendance = create_objects(
        #     Attendance.objects,
        #     teacher=user.teacher,
        #     student=student,
        #     grade=student.grade,
        #     mark_attendance=int(mark_attendance),
        #     date=date_attendance,
        #     reason=reason
        # )
        #
        # serializer = AttendanceSerializer(attendance)
        # return Response(serializer.data)


    serializer_class = AttendanceSerializer


class GradeViewSet(ModelViewSet):
    def get_object(self):
        # queryset = self.get_queryset()

        obj = get_object_or_404(Grade, pk=int(self.kwargs.get('pk')))
        # self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        queryset = Grade.objects.all()
        user = get_object_or_404(queryset, name=self.kwargs.get('pk'))
        serializer = GradeParentSerializer(user)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'teacher'):
            return Grade.objects.filter(teacher=user.teacher.id)
        elif hasattr(user, 'parent'):
            parent_students = Student.objects.filter(parent_id=user.parent.id)
            grade_names = set([student.grade.name for student in parent_students])
            return Grade.objects.filter(name__in=grade_names)

        # if user.is_staff:
        #     return all_objects(Grade.objects)
        #
        # try:
        #     if isinstance(user.teacher, Teacher):
        #         return Grade.objects.filter(teacher=user.teacher.id)
        # except:
        #     pass



    # serializer_class = GradeSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', ]

    def get_serializer_class(self, *args, **kwargs):
        if hasattr(self.request.user, 'parent'):
            return GradeParentSerializer
        return GradeSerializer


