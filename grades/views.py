from django.shortcuts import render
from . import models

# Create your views here.
def assignments(request):
    all_assignments = models.Assignment.objects.order_by("deadline")
    return render(request, "assignments.html", {'assignments': all_assignments})
def index(request, assignment_id):
    return render(request, "index.html")
def submissions(request, assignment_id):
    return render(request, "submissions.html")
def profile(request):
    return render(request, "profile.html")
def login_form(request):
    return render(request, "login.html")