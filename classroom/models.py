from django.db import models
import authentication

class Classroom(models.Model):
    class_id = models.UUIDField(primary_key=True)
    # member = models.CharField()
    #empid of the trainer
    trainer_id = models.ForeignKey(authentication.models.User)

class ClassMember(models.Model):
    class_id = models.ForeignKey(Classroom)
    member = models.ForeignKey(authentication.models.User)

class ClassCourse(models.Model):
    sno = models.AutoField(primary_key=True)
    class_id = models.ForeignKey(Classroom)
    
