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
    exclude_fields = []

    def __init__(self, *args, **kwargs):
        if len(kwargs) > 0:
            context = kwargs.get('context')
            if context:

                exclude_fields = context.get('exclude_fields')

                if exclude_fields:
                    # преобразование одного поля в массив, если передано только одно поле
                    if not isinstance(exclude_fields, (list, tuple)):
                        exclude_fields = [exclude_fields]

                self.exclude_fields = exclude_fields
        super().__init__(*args, **kwargs)

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)

        for field_name in self.exclude_fields:
            if field_name in fields:
                fields.pop(field_name)

        return fields

    class Meta:
        model = Student
        fields = '__all__'

    # def to_representation(self, instance):
    #     rep = super(StudentSerializer, self).to_representation(instance)
    #     # rep['grade'] = instance.grade.grade
    #     return rep