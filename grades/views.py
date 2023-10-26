from django.http import Http404
from django.shortcuts import render
from . import models

# Create your views here.
def assignments(request):
    all_assignments = models.Assignment.objects.order_by("deadline")
    return render(request, "assignments.html", {'assignments': all_assignments})
def index(request, assignment_id):
    try:
        asgn = models.Assignment.objects.get(pk=assignment_id)
        total_submissions = asgn.submission_set.count()
        submissions_assigned_to_you = asgn.submission_set.filter(grader__username="ta1").count()
        total_students = models.Group.objects.get(name="Students").user_set.count()
        return render(request, "index.html", {
            'assignment': asgn,
            'total_submissions': total_submissions,
            'submissions_assigned_to_you': submissions_assigned_to_you,
            'total_students': total_students,
        })
    except models.Assignment.DoesNotExist:
        raise Http404("Assignment not found")
    
def submissions(request, assignment_id):
    return render(request, "submissions.html")
def profile(request):
    return render(request, "profile.html")
def login_form(request):
    return render(request, "login.html")

def assignment_not_found(request, exception):
    return render(request, '404.html', status=404)