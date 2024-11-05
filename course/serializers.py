from rest_framework.serializers import ModelSerializer
from . import models

class QuestionSerializer(ModelSerializer):
    class Meta:
        model = models.Questions
        fields = '__all__'

class AssessmentSerializer(ModelSerializer):
    questions = QuestionSerializer(read_only=True,many=True)
    class Meta:
        model = models.Assesment
        fields = '__all__'
 
class ChapterSerializer(ModelSerializer):
    assessments = AssessmentSerializer(read_only=True,many=True)
    class Meta:
        model = models.Chapter
        fields = '__all__'

class ModuleSerializer(ModelSerializer):
    chapters = ChapterSerializer(read_only=True,many=True)
    class Meta:
        model = models.Module
        fields = '__all__'
 
class CourseSerializer(ModelSerializer):
    modules = ModuleSerializer(read_only=True,many=True)
    class Meta:
        model = models.Course
        fields = '__all__'
    