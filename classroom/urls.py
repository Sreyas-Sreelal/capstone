from django.urls import path
from . import views


urlpatterns = [
    path('create_classroom',views.create_classroom),
    path('delete_classroom',views.delete_classroom),
    path('view_classrooms',views.view_classrooms),
    path('get_available_trainers',views.get_available_trainers),
    path('get_available_employees',views.get_available_employees)
]