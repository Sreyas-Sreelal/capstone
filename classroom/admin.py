from django.contrib import admin
from .models import Classroom, Curriculum,Modules,Meetings


# Register your models here.
admin.site.register(Classroom)
admin.site.register(Curriculum)
admin.site.register(Modules)
# admin.site.register(ClassRoomAttendance)
# admin.site.register(UserAttendance)
admin.site.register(Meetings)