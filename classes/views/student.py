from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from classes.models.grade import Grade
from classes.models.student import Student
from classes.serializers.student import StudentSerializer, StudentParentSerializer
from common.services import all_objects, filter_objects


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