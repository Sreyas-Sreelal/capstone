from django.db import models
import uuid


class Course(models.Model):
    course_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    course_name = models.TextField(unique=True)
    course_type = models.CharField(max_length=20)
    deliverables = models.CharField(max_length=20)


class Module(models.Model):
    module_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    module_name = models.CharField(max_length=50)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)


class Chapter(models.Model):
    chapter_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    module_id = models.ForeignKey(Module, on_delete=models.CASCADE)
    chapter_name = models.CharField(max_length=50)
    chapter_content = models.TextField()
    # check
    # What if one chapter has more than one asst?
    # FK


class Assesment(models.Model):
    # PK
    question_id = models.AutoField(primary_key=True)
    chapter_id = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    question = models.TextField()
    option_1 = models.TextField()
    option_2 = models.TextField()
    option_3 = models.TextField()
    option_4 = models.TextField()
    correct_option = models.TextField()


class UserProgress(models.Model):
    user_id = models.ForeignKey(
        'authentication.User', on_delete=models.CASCADE)
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
