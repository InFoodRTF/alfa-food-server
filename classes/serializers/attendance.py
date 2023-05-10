from rest_framework.serializers import ModelSerializer

from classes.models.attendance import Attendance, AttendanceChoice
from classes.serializers.student import StudentSerializer


class AttendanceSerializer(ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

    def to_representation(self, instance):
        rep = super(AttendanceSerializer, self).to_representation(instance)
        rep['mark_attendance'] = AttendanceChoice(instance.mark_attendance).label
        rep['student'] = StudentSerializer().to_representation(instance.student)
        return rep