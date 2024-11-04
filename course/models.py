from django.db import models
import uuid

class Questions(models.Model):
    question_id = models.AutoField(primary_key=True)
    question = models.TextField()
    option_1 = models.TextField()
    option_2 = models.TextField()
    option_3 = models.TextField()
    option_4 = models.TextField()
    correct_option = models.TextField()

class Assesment(models.Model):
    # PK
    assessment_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    questions = models.ManyToManyField(Questions,related_name="assessment_questions")
    

class Chapter(models.Model):
    chapter_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    chapter_name = models.CharField(max_length=50)
    chapter_content = models.TextField()
    assessments = models.ManyToManyField(Assesment,related_name="chapter_assessments")
    # check
    # What if one chapter has more than one asst?
    # FK

class Module(models.Model):
    module_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    module_name = models.CharField(max_length=50)
    chapters = models.ManyToManyField(Chapter,related_name="module_chapters")

class Course(models.Model):
    course_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    course_name = models.TextField(unique=True)
    course_type = models.CharField(max_length=20)
    deliverables = models.CharField(max_length=20)
    modules = models.ManyToManyField(Module,related_name='course_modules')


class UserProgress(models.Model):
    user_id = models.ForeignKey(
        'authentication.User', 
        on_delete=models.CASCADE
    )
    chapter_id = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    score = models.IntegerField()
    attempted = models.BooleanField(default=False)

    # passstatus
    # employee id
    # assestment id
    # attemped
    # percentage (chapter)
    # score (out of 100)


class ChapterUser(models.Model):
    user_id = models.ForeignKey(
        'authentication.User', on_delete=models.CASCADE)
    chapter_id = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    # userid
    # chapterid
    # Attempted
