from django.db import models

class Classroom(models.Model):
    class_id = models.UUIDField(primary_key=True)
    # member = models.CharField()
    #empid of the trainer
    trainer_id = models.ForeignKey('authentication.User',on_delete=models.SET_NULL,null=True)

class ClassMember(models.Model):
    class_id = models.ForeignKey(Classroom,on_delete=models.CASCADE)
    member = models.ForeignKey('authentication.User',on_delete=models.SET_NULL,null=True)

class ClassCourse(models.Model):
    sno = models.AutoField(primary_key=True)
    class_id = models.ForeignKey(Classroom,on_delete=models.CASCADE)
    
