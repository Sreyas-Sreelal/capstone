from django.db import models

class Course(models.Model):
    course_id = models.UUIDField(primary_key=True)
    course_name = models.CharField(max_length=50)
    class_id = models.ForeignKey('classroom.class_id',on_delete=models.CASCADE)
    course_type = models.CharField(max_length=20)
    deliverables = models.CharField(max_length=20)

class Module(models.Model):
    module_id = models.UUIDField(primary_key=True)
    module_name = models.CharField(max_length=50)
    course_id = models.ForeignKey(Course,on_delete=models.CASCADE)

class Chapter(models.Model):
    chapter_id = models.UUIDField(primary_key=True)
    module_id = models.ForeignKey(Module,on_delete=models.CASCADE)
    chapter_name = models.CharField(max_length=50)
    #check 
    #What if one chapter has more than one asst?
    #FK
    assesment_id = models.UUIDField(unique=True)

class Assesment(models.Model):
    #PK
    question_id = models.AutoField(primary_key=True)
    assesment_id = models.ForeignKey(Chapter,to_field="assesment_id")
    chapter_id = models.ForeignKey(Chapter,on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    option_1 = models.CharField(max_length=500)
    option_2 = models.CharField(max_length=500)
    option_3 = models.CharField(max_length=500)
    option_4 = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=500)

class UserProgress(models.Model):
    pass
    #passstatus 
    # employee id
    #assestment id
    #attemped 
    # percentage (chapter)
    # score (out of 100)
    

class ChapterUser(models.Model):
    #userid
    #chapterid
    #Attempted
    pass
