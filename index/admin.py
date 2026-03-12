from django.contrib import admin
from .models import EClass, User, Student, Teacher, Exercise, Question, ExerciseResult, Thread, ChatMessage, Announcement, AnnouncementFile, Subject, GradeRecord

# Simple registration
admin.site.register(EClass)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Exercise)
admin.site.register(Question)
admin.site.register(ExerciseResult)
admin.site.register(Thread)
admin.site.register(ChatMessage)
admin.site.register(Announcement)
admin.site.register(AnnouncementFile)

admin.site.register(User)