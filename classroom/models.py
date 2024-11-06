from django.db import models
import uuid


class Modules(models.Model):
    module_id = models.UUIDField(primary_key=True,unique=True,default=uuid.uuid4)
    expected_meetings = models.IntegerField()
    module_name = models.TextField()
    detailed_description = models.TextField()


class Curriculum(models.Model):
    curriculum_id = models.UUIDField(
        default=uuid.uuid4, 
        unique=True, 
        primary_key=True
    )

    modules = models.ManyToManyField(
        Modules, 
        related_name="curriculum_modules"
    )


class Classroom(models.Model):
    class_id = models.UUIDField(
        primary_key=True, 
        unique=True, 
        default=uuid.uuid4
    )
    title = models.TextField(null=True)
    manager_id = models.ForeignKey(
        'authentication.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='class_manager'
    )
    # member = models.CharField()
    # empid of the trainer
    trainer_id = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True
    )
    members = models.ManyToManyField(
        'authentication.User', 
        related_name="class_members"
    )
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    eod = models.DateField()