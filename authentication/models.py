from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    class_id = models.ForeignKey(
        'classroom.Classroom',
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        blank=True
    )
    role = models.CharField(max_length=200, null=True)
    email_id = models.EmailField(unique=True)
    password = models.CharField(max_length=72)

    REQUIRED_FIELDS = ['email_id', 'password', 'role']
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email_id'

    is_anonymous = False


class Certifications(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    course_name = models.CharField(max_length=200, unique=True)
