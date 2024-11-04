from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from . import models
from . import serializer

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

        return Response({"ok": True, "course": serializer.CourseSerializer(new_course).data})
    except Exception as e:
        return Response({"ok": False, "error": str(e)})
