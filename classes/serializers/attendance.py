from rest_framework import serializers

from classes.models.attendance import Attendance, StudentAttendance, AttendanceChoice
from classes.serializers.grade import GradeSerializer
from classes.serializers.student import StudentSerializer





class StudentAttendanceSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели StudentAttendance
    """
    # attendance = AttendanceSerializer(read_only=True)
    student = StudentSerializer(read_only=True,  context={'exclude_fields': ['grade', 'parent_id']})

    class Meta:
        model = StudentAttendance
        exclude = ['attendance', ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['mark_attendance'] = AttendanceChoice(instance.mark_attendance).label
        # rep['student'] = instance.student.get_full_name()
        return rep


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Attendance
    """

    attended_students = StudentAttendanceSerializer(source='student_attendances', many=True, read_only=True,)

    class Meta:
        model = Attendance
        fields = '__all__'




# class GradeAttendanceSerializer(StudentAttendanceSerializer):
#     class Meta(StudentAttendanceSerializer.Meta):
#         fields = StudentAttendanceSerializer.Meta.fields

# from rest_framework.serializers import ModelSerializer
#
# from classes.models.attendance import Attendance, AttendanceChoice
# from classes.serializers.student import StudentSerializer
#
#
# class AttendanceSerializer(ModelSerializer):
#     class Meta:
#         model = Attendance
#         fields = '__all__'
#
#     def to_representation(self, instance):
#         rep = super(AttendanceSerializer, self).to_representation(instance)
#         rep['mark_attendance'] = AttendanceChoice(instance.mark_attendance).label
#         rep['student'] = StudentSerializer().to_representation(instance.student)
#         return rep