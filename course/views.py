from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from . import models
from . import serializers

# Create your views here.


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request: Request):
    """
    Request Format:
        {
            "course_name":"",
            "course_type":"",
            "deliverables":"",
            "modules":[
                {
                    "module_name":"",
                    "chapters":[
                        {
                            "chapter_name":"",
                            "assessments":[
                                {
                                    "questions":[
                                        {
                                            "question":"",
                                            "option_1":"",
                                            "option_2":"",
                                            "option_3":"",
                                            "option_4":"",
                                            "correct":""
                                        }
                                    ]
                                }
                            ]

                        }
                    ]
                }
            ]
        }
    """
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'admin':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)
    data = request.data
    try:
        new_course = models.Course(
            course_name=data['course_name'],
            course_type=data['course_type'],
            deliverables=data['deliverables']
        )
        new_course.save()

        for module in data['modules']:
            new_module = models.Module.objects.create(
                module_name=module['module_name'],
            )
            new_course.modules.add(new_module)

            for chapter in module['chapters']:
                new_chapter = models.Chapter.objects.create(
                    chapter_name=chapter['chapter_name'],
                )
                new_module.chapters.add(new_chapter)

                for assessments in chapter['assessments']:
                    new_assessment = models.Assesment.objects.create()
                    new_chapter.assessments.add(new_assessment)

                    for question in assessments['questions']:
                        new_question = models.Questions.objects.create(
                            question=question["question"],
                            option_1=question["option_1"],
                            option_2=question["option_2"],
                            option_3=question["option_3"],
                            option_4=question["option_4"],
                            correct_option=question["correct_option"],
                        )
                        new_assessment.questions.add(new_question)

        return Response({"ok": True, "course": serializers.CourseSerializer(new_course).data})
    except Exception as e:
        return Response({"ok": False, "error": str(e)})

# incredibly inefficient, but since time is not in favour, we can just go with it for now
# instead we should fetch only course ids and implement another routes for each course details
# may be we can use ViewSet to simplify? (thoughts for later!)
# also with pagination?
@api_view(['GET'])
def get_courses(request:Request):
    pass

class CourseViewSet(ModelViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True,methods=['GET'])
    def view_modules(self,request:Request,pk=None):
        modules = self.get_object().modules.all()
        return Response(serializers.ModuleSerializer(modules,many=True).data)

