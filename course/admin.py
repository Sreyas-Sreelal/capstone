from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Course)
admin.site.register(models.Chapter)
admin.site.register(models.Assesment)
admin.site.register(models.ChapterUser)
admin.site.register(models.UserProgress)