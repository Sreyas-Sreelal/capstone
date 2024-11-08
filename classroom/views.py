import datetime
from xml.etree.ElementInclude import include
from django.shortcuts import render
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from authentication.serializers import UserSerializer
from classroom.serializers import ClassroomSerializer, CurriculumSerializer, MeetingSerializer
from . import models
from . import serializers
from rest_framework_simplejwt.tokens import AccessToken
from authentication.models import User
from course.models import Course
from django.db import IntegrityError

# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_trainers(request: Request):
    trainers = User.objects.filter(role='trainer').all()
    response = Response()
    response.data = {"ok": True, "results": []}
    for trainer in trainers:
        response.data["results"].append(
            {"value": trainer.user_id, "label": trainer.username})
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_employees(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'manager':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    response = Response()
    response.data = {"ok": True, "results": []}

    members = User.objects.filter(manager_id=User(
        pk=access_token.payload['user_id'])).all()

    for member in members:
        response.data["results"].append(
            {"value": member.user_id, "label": member.username})

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_classroom(request: Request):
    """
    Request Format:
    {
        "title":"",
        "trainer_id":"",
        "members":[
            "",
        ],
        "curriculum":{
            "name":"",
            "modules":[
                {
                    "expected_meetings":0,
                    "module_name":"",
                    "detailed_description":"",
                }
            ]
        },
        "eod":""
    }
    """

    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'manager':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    user: User = User.objects.get(user_id=request.data['trainer_id'])
    if user.role != 'trainer':
        return Response({"ok": False, "error": "Specified user is not a trainer!"}, status=500)

    new_curriculum = models.Curriculum.objects.create()

    for module in request.data['modules']:
        new_module = models.Modules.objects.create(
            expected_meetings=module['expected_meetings'],
            module_name=module['module_name'],
            detailed_description=module['detailed_description']
        )
        new_curriculum.modules.add(new_module)

    new_class = models.Classroom.objects.create(
        curriculum_id=new_curriculum.curriculum_id,
        title=request.data['title'],
        trainer_id=User(pk=request.data['trainer_id']),
        manager_id=User(pk=access_token.payload['user_id']),
        start_date=request.data['start_date'],
        eod=request.data['eod']
    )
    new_class.save()

    for member in request.data['members']:
        new_class.members.add(User.objects.get(pk=member))
    return Response({"ok": True})


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_classrooms(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'manager':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    classrooms = models.Classroom.objects.filter(
        manager_id=access_token.payload['user_id']
    ).all()

    return Response({"ok": True, "classrooms": ClassroomSerializer(classrooms, many=True).data})


class CurriculumViewset(viewsets.ModelViewSet):
    queryset = models.Curriculum.objects.all()
    serializer_class = serializers.CurriculumSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['GET'])
    def view_module(self, request: Request, pk=None):
        modules = self.get_object().modules.all()
        return Response(serializers.ModuleSerializer(modules, many=True).data)


class ClasroomViewset(viewsets.ModelViewSet):
    queryset = models.Classroom.objects.all()
    serializer_class = serializers.ClassroomSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['GET'])
    def view_curriculum(self, request: Request, pk=None):
        return Response(serializers.CurriculumSerializer(self.get_object().curriculum).data)


@api_view(['POST'])
def get_employees_under_trainer(request: Request):
    access_token = AccessToken(request.headers['token'])

    classroom = models.Classroom.objects.filter(
        trainer_id=access_token.payload['user_id']).first()

    response = Response(data={})
    response.data["ok"] = True

    response.data["members"] = UserSerializer(
        classroom.members,
        many=True,
        include=['username', 'user_id']
    ).data

    classroom = models.Classroom.objects.filter(
        trainer_id=access_token.payload['user_id']
    ).get()

    today_date = request.data.get('date', datetime.date.today())
    (class_attendance, created) = models.ClassRoomAttendance.objects.get_or_create(
        date=today_date, classroom_id=classroom,)
    print("created is", created)
    if created:
        for member in classroom.members.all():
            class_attendance.employee_status.add(models.UserAttendance.objects.create(
                user=member,
                present_status=False,
            ))

    employees = class_attendance.employee_status.all()

    for member in response.data["members"]:
        present_status = class_attendance.employee_status.filter(
            user_id=member['user_id']).get().present_status
        member['present'] = present_status
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_attendance(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'trainer':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)
    classroom = models.Classroom.objects.filter(
        trainer_id=access_token.payload['user_id']).get()

    today_date = request.data.get('date', datetime.date.today())

    class_attendance = None
    if not models.ClassRoomAttendance.objects.filter(date=today_date, classroom_id=classroom).exists():
        class_attendance = models.ClassRoomAttendance.objects.create(
            classroom_id=classroom,
        )
    else:
        class_attendance = models.ClassRoomAttendance.objects.filter(
            date=today_date).get()

        existing_attendance = class_attendance.employee_status.all()
        for attendance in existing_attendance:
            attendance.delete()

        class_attendance.employee_status.clear()

    for user in request.data['users']:
        class_attendance.employee_status.add(models.UserAttendance.objects.create(
            user=User.objects.filter(user_id=user['user_id']).get(),
            present_status=user['present'],
        ))

    return Response({"ok": True, "results": serializers.ClassRooomAttendanceSerializer(class_attendance).data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_absentees_list(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'trainer':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    today_date = datetime.date.today()

    classroom = models.Classroom.objects.filter(
        trainer_id=access_token.payload['user_id']).get()

    if not models.ClassRoomAttendance.objects.filter(date=today_date, classroom_id=classroom).exists():
        return Response({"ok": False, "error": "Attendance hasn't been marked for today!"})
    else:
        class_attendance = models.ClassRoomAttendance.objects.filter(
            date=today_date).get()
        employee_status = class_attendance.employee_status.all()
        users = []
        for user in employee_status:
            if not user.present_status:
                users.append(User.objects.filter(user_id=user.user_id).get())
        if len(users) > 0:
            return Response({"ok": True, "absentees": UserSerializer(users, many=True, include=['user_id', 'username']).data})
        else:
            return Response({"ok": False, "error": "No Absenteess today!"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schedule_meeting(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'trainer':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)
    classroom = models.Classroom.objects.filter(
        trainer_id=access_token.payload['user_id']).get()
    try:
        meeting = models.Meetings.objects.create(
            meeting_name=request.data['meeting_name'],
            meeting_date=request.data['meeting_date'],
            meeting_link=request.data['meeting_link'],
            start_time=request.data['start_time'],
            end_time=request.data['end_time'],
            trainer_id=User(pk=access_token.payload['user_id']),
            classroom_id=classroom
        )
        return Response({"ok": True, "meeting": MeetingSerializer(meeting).data})
    except IntegrityError as e:
        meeting = models.Meetings.objects.get(
            meeting_date=request.data['meeting_date'],
            trainer_id=User(pk=access_token.payload['user_id']),
            classroom_id=classroom
        )
        meeting.delete()

        meeting = models.Meetings.objects.create(
            meeting_name=request.data['meeting_name'],
            meeting_date=request.data['meeting_date'],
            meeting_link=request.data['meeting_link'],
            start_time=request.data['start_time'],
            end_time=request.data['end_time'],
            trainer_id=User(pk=access_token.payload['user_id']),
            classroom_id=classroom
        )
        return Response({"ok": True, "meeting": MeetingSerializer(meeting).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_meeting(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'trainer':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    models.Meetings.objects.filter(
        pk=request.data['meeting_id']).delete()
    return Response({"ok": True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def attend_meeting(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'employee':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    meeting = models.Meetings.objects.filter(
        meeting_id=request.data['meeting_id']).get()
    if meeting.participants.filter(pk=access_token.payload['user_id']).exists():
        return Response({"ok": False, "error": "You already attended this meeting"})
    meeting.participants.add(User.objects.filter(
        pk=access_token.payload['user_id']).get())

    return Response({"ok": True, "meeting": MeetingSerializer(meeting).data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_meetings(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] == 'trainer':
        classroom = models.Classroom.objects.filter(
            trainer_id=access_token.payload['user_id']).get()
    elif access_token.payload['role'] == 'employee':
        classroom = models.Classroom.objects.get(
            pk=(User.objects.get(pk=access_token.payload['user_id']).class_id.class_id))

    if request.data.get('meeting_date') == None:
        meetings = models.Meetings.objects.filter(classroom_id=classroom).all()

        return Response({"ok": True, "meetings": MeetingSerializer(meetings, many=True).data})
    else:
        meetings = models.Meetings.objects.filter(
            meeting_date=request.data['meeting_date'],
            classroom_id=classroom
        ).all()

        return Response({"ok": True, "meetings": MeetingSerializer(meetings, many=True).data})


@api_view(['GET'])
def get_manager_dashboard_details(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'manager':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    response = Response()
    response.data = {}
    response.data['ok'] = True
    classrooms_query = models.Classroom.objects.filter(
        manager_id=access_token.payload['user_id']
    )
    response.data['classroom_count'] = classrooms_query.count()

    available_classrooms = classrooms_query.all()
    response.data['classes'] = ClassroomSerializer(
        available_classrooms, many=True).data

    for classroom in response.data['classes']:
        start_date = datetime.datetime.strptime(
            classroom['start_date'], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(classroom['eod'], '%Y-%m-%d')
        classroom['progress'] = ((datetime.datetime.today(
        ) - start_date).days / (end_date - start_date).days) * 100
    response.data['employee_count'] = User.objects.filter(
        manager_id=access_token.payload['user_id'], role='employee').count()

    response.data['trainer_count'] = User.objects.filter(
        manager_id=access_token.payload['user_id'], role='trainer').count()

    return response
