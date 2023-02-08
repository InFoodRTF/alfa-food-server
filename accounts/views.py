from django.contrib.auth.models import Group
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from knox.models import AuthToken

from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, CanteenEmployeeSerializer, \
    TeacherSerializer, ParentSerializer
from .services import roles


class UserAPIView(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()

        user = self.request.user

        if hasattr(user, 'parent'):
            user = user.parent
            serializer_class = ParentSerializer
        elif hasattr(user, 'teacher'):
            user = user.teacher
            serializer_class = TeacherSerializer
        elif hasattr(user, 'canteenemployee'):
            user = user.canteenemployee
            serializer_class = CanteenEmployeeSerializer

        kwargs['context'] = self.get_serializer_context()

        return serializer_class(user, **kwargs)

    # def get_serializer_class(self):
    #     user = self.request.user
    #     if hasattr(user, 'parent'):
    #         user = user.parent
    #         return ParentSerializer
    #     elif hasattr(user, 'teacher'):
    #         return TeacherSerializer(user.teacher)
    #     elif hasattr(user, 'canteenemployee'):
    #         return CanteenEmployeeSerializer(user.canteenemployee)


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        try:
            role = request.data.get('role')
            group = Group.objects.get(name=role)
        except Group.DoesNotExist:
            return Response({'username': 'Невозможно присвоить роль пользователю или роли не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            # "token": AuthToken.objects.create(user)[1]
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            # "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

