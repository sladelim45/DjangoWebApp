from django.contrib import admin
from grades.models import Assignment, Submission

# Register your models here.
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'deadline', 'weight', 'points']
    list_filter = ['deadline']
    search_fields = ['title', 'description']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'author', 'grader', 'score']
    list_filter = ['assignment', 'grader']
    search_fields = ['assignment__title', 'author__username']