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
from course.serializers import ModuleSerializer
from . import models
from . import serializers
from rest_framework_simplejwt.tokens import AccessToken
from authentication.models import User
from django.db import IntegrityError
from django.db.models import Q

# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_trainers(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'manager':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)
    trainers = list(User.objects.filter(role='trainer').all())
    classroms = models.Classroom.objects.all()
    for classes in classroms:
        trainers.remove(classes.trainer_id)
    print(list(trainers))
    
    response = Response()
    response.data = {"ok": True, "results": []}
    for trainer in trainers:
        print("asd",trainer)
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
        pk=access_token.payload['user_id']), role='employee').filter(Q(class_id_id=None)).all()

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
        user = User.objects.get(pk=member)
        user.class_id = new_class
        user.save()
        new_class.members.add(user)
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
def get_employees_attendance_list(request: Request):
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

    if not models.Meetings.objects.filter(meeting_date=today_date, trainer_id=access_token.payload['user_id'], classroom_id=classroom).exists():
        return Response({"ok": False, "error": "No meetings held today!"})

    meeting = models.Meetings.objects.filter(
        meeting_date=today_date, trainer_id=access_token.payload['user_id'], classroom_id=classroom).get()
    participants = meeting.participants.all()
    for member in response.data["members"]:
        user = User.objects.filter(pk=member['user_id']).get()
        # print(user,employees)
        member['present'] = user in participants

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

    if not models.Meetings.objects.filter(trainer_id=access_token.payload['user_id'], meeting_date=today_date, conducted=True).exists():
        return Response({"ok": False, "error": "No meeting held today!"})

    meeting = models.Meetings.objects.filter(meeting_date=today_date, trainer_id=access_token.payload['user_id']).get()
    participants = meeting.participants.all()

    for user in request.data['users']:
        user_obj = User.objects.get(pk=user['user_id'])
        if user['present']:
            if user_obj not in participants:
                meeting.participants.add(
                    User.objects.filter(user_id=user['user_id']).get())
        else:
            if user_obj in participants:
                meeting.participants.remove(user_obj)
    return Response({"ok": True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_absentees_list(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'trainer':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    today_date = datetime.date.today()

    if not models.Meetings.objects.filter(trainer_id=access_token.payload['user_id'], meeting_date=today_date, conducted=True).exists():
        return Response({"ok": False, "error": "No meeting held today!"})

    classroom = models.Classroom.objects.filter(
        trainer_id=access_token.payload['user_id']).get()

    users = []

    meeting = models.Meetings.objects.filter(meeting_date=today_date,trainer_id=access_token.payload['user_id'], conducted=True).get()

    participants = meeting.participants.all()

    for user in classroom.members.all():
        if not user in participants:
            users.append(user)
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
        meeting.participants.clear()
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
    if access_token.payload['role'] != 'employee' and access_token.payload['role'] != 'trainer':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    meeting = models.Meetings.objects.filter(
        meeting_id=request.data['meeting_id']
    ).get()

    if access_token.payload['role'] == 'trainer' and meeting.trainer_id.user_id == access_token.payload['user_id']:
        meeting.conducted = True
        meeting.save()
        # classroom = models.Classroom.objects.filter(
        #     trainer_id=access_token.payload['user_id']
        # ).get()
        # (class_attendance,created) = models.ClassRoomAttendance.objects.get_or_create(
        #     classroom_id=meeting.classroom_id,
        # )
        # for member in classroom.members.all():
        #     print("adding",member)
        #     class_attendance.employee_status.add(models.UserAttendance.objects.create(
        #         user=member,
        #         present_status=False,
        #     ))

    else:
        if not meeting.conducted:
            return Response({"ok": False, "error": "This meeting is not started yet!"})
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
@permission_classes([IsAuthenticated])
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
    response.data['classes'] = []
    for classes in available_classrooms:
        curriculum = classes.curriculum
        modules = curriculum.modules.all()
        total_expected_meetings = 0
        for module in modules:
            total_expected_meetings += module.expected_meetings
        response.data['classes'].append(ClassroomSerializer(classes).data)
        response.data['classes'][-1]['meeting_count'] = models.Meetings.objects.filter(
            classroom_id=classes, conducted=True).count()
        response.data['classes'][-1]['progress'] = (
            response.data['classes'][-1]['meeting_count'] / total_expected_meetings) * 100
        response.data['classes'][-1]['employee_count'] = classes.members.count()
        response.data['classes'][-1]['trainer_name'] = classes.trainer_id.username
        modules = []
        for module in classes.curriculum.modules.all():
            modules.append(ModuleSerializer(module).data)

        response.data["classes"][-1]["modules"] = modules

        meetings = models.Meetings.objects.filter(
            classroom_id=classes, conducted=True).all()
        meeting_count = models.Meetings.objects.filter(
            classroom_id=classes, conducted=True).count()
        response.data['employees_under_manager_count'] = User.objects.filter(
            manager_id=access_token.payload['user_id'], role='employee').count()

        # get all meetings
        if meeting_count > 0:
            total_employees = classes.members.count()
            avg = 0

            for meeting in meetings:
                avg += (meeting.participants.count() / total_employees) * 100
            print(avg,meeting_count)
            avg /= meeting_count
            print(avg)
            #avg *= 100
            response.data['classes'][-1]['average_attendance'] = avg
        else:
            response.data['classes'][-1]['average_attendance'] = 0
    for classroom in response.data['classes']:
        start_date = datetime.datetime.strptime(
            classroom['start_date'], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(classroom['eod'], '%Y-%m-%d')
        classroom['completion_timeline'] = ((datetime.datetime.today(
        ) - start_date).days / (end_date - start_date).days) * 100

    response.data['trainer_count'] = User.objects.filter(
        manager_id=access_token.payload['user_id'], role='trainer').count()

    response.data['employees_not_under_training'] = User.objects.filter(
        manager_id=access_token.payload['user_id'], role='employee').filter(Q(class_id=None)).count()
    response.data['employees_under_training'] = response.data['employees_under_manager_count'] - \
        response.data['employees_not_under_training']

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employees_under_manager(request: Request,query=""):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'manager':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    if query != "":
        employees = User.objects.filter(
            manager_id=access_token.payload['user_id'], role='employee',username__contains=query).all()
    else:    
        employees = User.objects.filter(
            manager_id=access_token.payload['user_id'], role='employee').all()

    response = Response(data={})
    response.data["ok"] = True
    response.data["employees"] = []

    for employee in employees:
        response.data["employees"].append(UserSerializer(
            employee, include=['username', 'user_id']).data)
        if employee.class_id:
            response.data["employees"][-1]["classroom"] = employee.class_id.title
        else:
            response.data["employees"][-1]["classroom"] = "Not enrolled in any Classes"

        meetings = models.Meetings.objects.filter(
            classroom_id=employee.class_id, conducted=True).all()
        total_meetings = models.Meetings.objects.filter(
            classroom_id=employee.class_id, conducted=True).count()
        attended_meetings = 0
        for meeting in meetings:
            if employee in meeting.participants.all():
                attended_meetings += 1
        if total_meetings != 0:
            response.data["employees"][-1]["attendance_percentage"] = (
                attended_meetings/total_meetings) * 100
        else:
            response.data["employees"][-1]["attendance_percentage"] = 0
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trainer_details_for_manager(request: Request):
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'manager':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    trainers = User.objects.filter(
        manager_id=access_token.payload['user_id'], role='trainer').all()

    response = Response(data={})

    response.data['ok'] = True
    response.data['trainers'] = []
    for trainer in trainers:
        response.data['trainers'].append(UserSerializer(
            trainer, include=["username", "user_id"]).data)
        meeting_details = {}
        meetings = models.Meetings.objects.filter(trainer_id=trainer).all()
        classroom = models.Classroom.objects.filter(trainer_id=trainer).first()
        if classroom:
            response.data['trainers'][-1]['classroom'] = classroom.title
        else:
            response.data['trainers'][-1]['classroom'] = 'Currently not teaching'
        response.data['trainers'][-1]['meetings'] = MeetingSerializer(
            meetings, many=True).data

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_details(request: Request):
    response = Response(data={})
    response.data['ok'] = True
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'employee':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    user = User.objects.filter(pk=access_token.payload['user_id']).get()
    response.data['user'] = UserSerializer(
        user, include=['username', 'user_id']).data

    response.data['classroom'] = ClassroomSerializer(user.class_id).data
    response.data['trainer'] = user.class_id.trainer_id.username
    response.data['manager'] = user.class_id.manager_id.username
    meetings = models.Meetings.objects.filter(
        trainer_id=user.class_id.trainer_id, classroom_id=user.class_id).all()
    meeting_count = models.Meetings.objects.filter(
        trainer_id=user.class_id.trainer_id, classroom_id=user.class_id).count()
    total = 0
    for meeting in meetings:
        participants = meeting.participants.all()
        if user in participants:
            total += 1
    if meeting_count !=0:
        response.data['attendance'] = (total/meeting_count) * 100
    else:
        response.data['attendance'] = 0

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trainer_dashboard_details(request: Request):
    response = Response(data={})
    response.data["ok"] = True
    access_token = AccessToken(request.headers['token'])
    if access_token.payload['role'] != 'trainer':
        return Response({"ok": False, "error": "You are not allowed to perform this operation"}, status=401)

    trainer = User.objects.get(pk=access_token.payload['user_id'])
    classroom = models.Classroom.objects.filter(trainer_id=trainer).get()
    response.data['user'] = UserSerializer(
        trainer, include=['username', 'user_id']).data
    response.data['classroom'] = ClassroomSerializer(classroom).data
    meetings = models.Meetings.objects.filter(
        trainer_id=trainer, classroom_id=classroom, conducted=True).all()
    response.data['meetings_conducted'] = meetings.count()
    
    total_employees = classroom.members.count()
    response.data['total_students'] = total_employees

    meeting_count = response.data['meetings_conducted']
    
    response.data['average_attendance'] = 0
    if meeting_count >0:
        avg = 0
        for meeting in meetings:
            avg += meeting.participants.count() / total_employees
        avg /= meeting_count
        avg *= 100
        response.data['average_attendance'] = avg
    
    total_expected = 0
    response.data['percent_progress'] = 0

    for module in classroom.curriculum.modules.all():
        total_expected += module.expected_meetings
    print("total expeted",total_expected)
    if total_expected > 0:
        response.data['percent_progress'] =int ((
            response.data['meetings_conducted']/total_expected)*100)
    

    return response
