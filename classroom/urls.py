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
    path('update_attendance',views.update_attendance)
]

router = DefaultRouter()
router.register('view_curriculum',views.CurriculumViewset)

urlpatterns += router.urls