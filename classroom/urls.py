from django.urls import path
from . import views


urlpatterns = [
    path('create_classroom',views.create_classroom),
    path('delete_classroom',views.delete_classroom),
    path('view_classrooms',views.view_classrooms),
]