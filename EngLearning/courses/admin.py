from django.contrib import admin
from .models import *

# Register your models here.
class TagAdmin(admin.TabularInline):
    model = Tag

class PrerequisiteAdmin(admin.TabularInline):
    model = Prerequisite

class LearningsAdmin(admin.TabularInline):
    model = Learnings 

class VideoAdmin(admin.TabularInline):
    model = Video

class CourseAdmin(admin.ModelAdmin):
    inlines = [TagAdmin, LearningsAdmin, PrerequisiteAdmin, VideoAdmin]

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson)
admin.site.register(Payment)
admin.site.register(UserCourse)