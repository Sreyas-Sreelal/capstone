from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('create_classroom',views.create_classroom),
    path('delete_classroom',views.delete_classroom),
    path('view_classrooms',views.view_classrooms),
    path('get_available_trainers',views.get_available_trainers),
    path('get_available_employees',views.get_available_employees),
    path('get_employees_under_trainer',views.get_employees_under_trainer),
    path('update_attendance',views.update_attendance),
    path('get_absentees_list',views.get_absentees_list),
    path('schedule_meeting',views.schedule_meeting),
    path('remove_meeting',views.remove_meeting),
    path('attend_meeting',views.attend_meeting),
    path('get_meetings',views.get_meetings),
    path('get_manager_dashboard_details',views.get_manager_dashboard_details)
]

router = DefaultRouter()
router.register('view_curriculum',views.CurriculumViewset)
router.register('view_classes',views.ClasroomViewset)
urlpatterns += router.urls