from django.db import models
import uuid


class Classroom(models.Model):
    class_id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4)
    title = models.TextField(null=True)
    manager_id = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL, null=True, related_name='class_manager')
    # member = models.CharField()
    # empid of the trainer
    trainer_id = models.ForeignKey(
        'authentication.User', 
        on_delete=models.SET_NULL, 
        null=True)
    members = models.ManyToManyField('authentication.User',related_name="class_members")
    courses = models.ManyToManyField('course.Course',related_name="class_courses")
