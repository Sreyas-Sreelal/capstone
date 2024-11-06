from http.client import responses
from urllib import response
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
import authentication
import classroom
# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_data(request: Request):
    access_token = AccessToken(request.headers['token'])
    classrooms = classroom.models.Classroom.object(
        manager_id=access_token.payload['user_id'])
    response = Response()

    response.data['ok'] = True

    response.data['employees_count'] = authentication.models.User.objects.filter(
        manager_id=access_token.payload['user_id']).count()
    response.data['classroom_count'] = classroom.models.Classroom.objects.filter(
        manager_id=access_token.payload['user_id']
    ).count()

    return responses