from rest_framework.serializers import ModelSerializer

from classes.models.student import Student


class StudentParentSerializer(ModelSerializer):
    class Meta:
        model = Student
        exclude = ['parent_id',]

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