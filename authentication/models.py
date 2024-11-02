from django.db import models
from django.contrib.auth.models import AbstractBaseUser
import classroom
# Create your models here.


class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=100)
    class_id = models.ForeignKey(classroom.models.Classroom)
    role = models.CharField(max_length=200)
    email_id = models.EmailField(unique=True)
    password = models.CharField(max_length=72)


class Certifications(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    course_name = models.CharField(max_length=200, unique=True)
