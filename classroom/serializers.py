from rest_framework import serializers

from course.serializers import ModuleSerializer
from . import models
from authentication.serializers import UserSerializer

class ModulesSerialier(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = models.Modules

class CurriculumSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True,read_only=True)
    class Meta:
        fields = "__all__"
        model = models.Curriculum        

class ClassroomSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True,read_only=True,include=['username','user_id'])
    class Meta:
        fields = "__all__"
        model = models.Classroom        

# class UserAttendanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = '__all__'
#         model = models.UserAttendance

# class ClassRooomAttendanceSerializer(serializers.ModelSerializer):
#     employee_statues = UserAttendanceSerializer(many=True,read_only=True)
#     class Meta:
#         fields = '__all__'
#         model = models.ClassRoomAttendance

class MeetingSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True,read_only=True,include=['username','user_id'])
    class Meta:
        fields = '__all__'
        model = models.Meetings
