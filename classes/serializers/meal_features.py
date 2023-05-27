from rest_framework.serializers import ModelSerializer
from classes.models.meal_features import MealTime


class MealTimeSerializer(ModelSerializer):
    class Meta:
        model = MealTime
        exclude = ['id']

    def to_representation(self, instance):
        rep = super(MealTimeSerializer, self).to_representation(instance)
        rep['meal_category'] = instance.meal_category.category_name
        return rep