from django.urls import path,include
from . import views
from rest_framework import routers

urlpatterns = [
    path('create',views.create_course)
]

router = routers.DefaultRouter()
router.register('view',views.CourseViewSet)

urlpatterns += [
    path('',include(router.urls))
]

