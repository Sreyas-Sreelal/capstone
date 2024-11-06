from django.urls import path
from . import views

urlpatterns = [
    path('get_dashboard_data',views.get_dashboard_data)
]
