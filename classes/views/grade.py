from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from classes.models.grade import Grade
from classes.models.student import Student
from classes.serializers.grade import GradeParentSerializer, GradeSerializer


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