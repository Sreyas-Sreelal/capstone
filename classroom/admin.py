from django.contrib import admin
from .models import Classroom, Curriculum,Modules


# Register your models here.
admin.site.register(Classroom)
admin.site.register(Curriculum)
admin.site.register(Modules)