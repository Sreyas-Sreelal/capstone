from django.db import models


class Classroom(models.Model):
    class_id = models.UUIDField(primary_key=True)
    title = models.TextField(null=True)
    manager_id = models.ForeignKey('authentication.User',on_delete=models.SET_NULL,null=True,related_name='class_manager')
    # member = models.CharField()
    # empid of the trainer
    trainer_id = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL, null=True)

# Stores relation between class and many users
class ClassMember(models.Model):
    class_id = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    member = models.ForeignKey(
        'authentication.User', on_delete=models.CASCADE, null=True)

# Stores relation between a class and many courses
class ClassCourse(models.Model):
    sno = models.AutoField(primary_key=True)
    class_id = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    #course_id = models.ForeignKey('course.Course', on_delete=models.CASCADE)
