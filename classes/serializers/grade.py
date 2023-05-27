from rest_framework.serializers import ModelSerializer

from accounts.models import Teacher
from classes.models.grade import Grade
from classes.serializers.meal_features import MealTimeSerializer


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