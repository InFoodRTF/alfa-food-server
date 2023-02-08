from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group

from rest_framework import serializers, status
from rest_framework.response import Response

from accounts.models import Profile, Parent, Teacher, CanteenEmployee, Administrator
from accounts.services import roles, set_user_name


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('middle_name',)


ROLE_CHOICES = (
    (Administrator, 0),
    (Teacher, 1),
    (CanteenEmployee, 2),
    (Parent, 3),
)


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    # groups = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='name',
    #  )

    # groups = RoleSerializer(many=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'profile')

    def to_representation(self, instance):
        rep = super(UserSerializer, self).to_representation(instance)

        rep.update(rep['profile'])
        rep.pop('profile')

        roles_arr = ['administrator', 'teacher', 'canteenemployee', 'parent']

        for role in roles_arr:
            if hasattr(instance, role):
                rep.update({"role": roles_arr.index(role)})  # 0|1|2|3 - index of role
                break

        return rep


def change_user_representation(rep, *args):
    rep.update(rep.pop('user'))

    return rep

class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Parent
        exclude = ['id']

    def to_representation(self, instance):
        rep = super(ParentSerializer, self).to_representation(instance)

        # Красивое представление данных
        rep = change_user_representation(rep)

        return rep


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Teacher
        exclude = ['id']

    def to_representation(self, instance):
        rep = super(TeacherSerializer, self).to_representation(instance)

        # Красивое представление данных
        rep = change_user_representation(rep)

        return rep


class CanteenEmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CanteenEmployee
        exclude = ['id']

    def to_representation(self, instance):
        rep = super(CanteenEmployeeSerializer, self).to_representation(instance)

        # Красивое представление данных
        rep = change_user_representation(rep)

        return rep


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        try:
            role = self.initial_data.get('role')
            group = Group.objects.get(name=role)
            role_model = roles.get(role)
        except Group.DoesNotExist:
            return Response({'username': 'Невозможно присвоить роль пользователю или роли не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )

        user.groups.add(group)

        set_user_name(self.initial_data, user)

        role_model.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")
