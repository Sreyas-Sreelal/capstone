from django.shortcuts import render
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from . import models
from rest_framework_simplejwt.tokens import AccessToken
from authentication.models import User


# Create your views here.


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_classroom(request: Request):
    """
    Request Format:
    {
        "trainer_id":"",
        "members":[
            "",
        ],
        "courses":[
            "",
        ]
    }
    """

    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'manager':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    try:
        user: User = User.objects.get(user_id=request.data['trainer_id'])
        if user.role != 'trainer':
            return Response({"ok": False, "error": "Specified user is not a trainer!"}, status=500)

        new_class = models.Classroom(
            title=request.data['title'],
            trainer_id=User(pk=request.data['trainer_id']),
            manager_id=User(pk=access_token.payload['user_id'])
        )
        new_class.save()

        for member in request.data['members']:
            models.ClassMember(class_id=new_class,
                               member=User(pk=member)).save()
        for course in request.data['members']:
            models.ClassCourse(class_id=new_class,
                               course_id=course).save()
    except Exception as e:
        print("Error", e)
        return Response({"ok": False, "error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_classroom(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'manager':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)
    try:
        classroom: models.Classroom = models.Classroom.objects.get(
            pk=request.data['class_id'])
        print(model_to_dict(classroom))
        if access_token.payload['user_id'] != classroom.manager_id:
            return Response({"ok": False, "error": "This classroom doesn't fall under your jurisdiction"}, status=401)

        classroom.delete()
        return Response({"ok": True})

    except Exception as e:
        print("Error", e)
        return Response({"ok": False, "error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def view_classrooms(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'manager':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    classrooms = models.Classroom.objects.filter(
        manager_id=access_token.payload['user_id']).all()

    return Response({"ok": True, "classrooms": list(map(model_to_dict, classrooms))})
