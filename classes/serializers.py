from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from accounts.models import Teacher
from classes.models import Student, Attendance, Grade, AttendanceChoice, MealTime, MealCategory


class StudentParentSerializer(ModelSerializer):
    class Meta:
        model = Student
        exclude = ['parent_id', 'id']

    def to_representation(self, instance):
        # TODO: Используй то что ниже, для вывода (возможно в абстрактный класс, чтобы все работало везде)
        #self.context['request'].user
        # self.Meta.exclude.pop(0)
        rep = super(StudentParentSerializer, self).to_representation(instance)
        rep['grade'] = instance.grade.name
        return rep


class StudentSerializer(ModelSerializer):

    class Meta:
        model = Student
        fields = '__all__'

    # def to_representation(self, instance):
    #     rep = super(StudentSerializer, self).to_representation(instance)
    #     # rep['grade'] = instance.grade.grade
    #     return rep


class MealTimeSerializer(ModelSerializer):
    class Meta:
        model = MealTime
        exclude = ['id']

    def to_representation(self, instance):
        rep = super(MealTimeSerializer, self).to_representation(instance)
        rep['meal_category'] = instance.meal_category.category_name
        return rep


class GradeParentSerializer(ModelSerializer):
    class Meta:
        model = Grade
        # fields = '__all__'
        exclude = ['id']

    def to_representation(self, instance):
        rep = super(GradeParentSerializer, self).to_representation(instance)
        rep['teacher'] = Teacher.objects.get(id=rep['teacher']).get_full_name()
        rep['meal_time'] = MealTimeSerializer(many=True).to_representation(instance.meal_time)
        return rep

class GradeSerializer(ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'

    def to_representation(self, instance):
        rep = super(GradeSerializer, self).to_representation(instance)
        rep['meal_time'] = MealTimeSerializer(many=True).to_representation(instance.meal_time)
        return rep


class AttendanceSerializer(ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

    def to_representation(self, instance):
        rep = super(AttendanceSerializer, self).to_representation(instance)
        rep['mark_attendance'] = AttendanceChoice(instance.mark_attendance).label
        rep['student'] = StudentSerializer().to_representation(instance.student)
        return rep
