from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.shortcuts import redirect, render
from . import models

# Create your views here.
def assignments(request):
    all_assignments = models.Assignment.objects.order_by("deadline")
    return render(request, "assignments.html", {
        'assignments': all_assignments
    })

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
    try:
        asgn = models.Assignment.objects.get(pk=assignment_id)
        submissions = asgn.submission_set.filter(grader__username="ta1").order_by("author__username")
        return render(request, "submissions.html", {
            'assignment': asgn,
            'submissions': submissions
        })
    except models.Assignment.DoesNotExist:
        raise Http404("Assignment not found")
    except models.Submission.DoesNotExist:
        raise Http404("Submission not found")

def profile(request):
    assignments = models.Assignment.objects.order_by("deadline")
    assignments_and_counts = []

    for assignment in assignments:
        count = "Not due"
        if timezone.now() > assignment.deadline:
            count = f'{assignment.submission_set.filter(grader__username="ta1", score__isnull=False).count()}/{assignment.submission_set.filter(grader__username="ta1").count()}'
        assignments_and_counts.append({'assignment': assignment, 'count': count})

    return render(request, "profile.html", {
        'assignments_and_counts': assignments_and_counts
    })

def login_form(request):
    return render(request, "login.html")

@require_POST
def grade(request, assignment_id):
    try:
        asgn = models.Assignment.objects.get(pk=assignment_id)
        submissions = asgn.submission_set.filter(grader__username="ta1")
        for key in request.POST:
            if key.startswith("grade-"):
                submission_id = int(key.split("-")[1])
                submission = submissions.get(id=submission_id)
                try:
                    score = float(request.POST[key])
                    submission.score = score
                except ValueError:
                    submission.score = None
                submission.save()
        return redirect(f"/{asgn.id}/submissions")
    except models.Assignment.DoesNotExist:
        raise Http404("Assignment not found")  
    except models.Submission.DoesNotExist:
        raise Http404("Submission not found")
        
# only is called when DEBUG is False in settings.py
def assignment_not_found(request, exception=None):
    return HttpResponse("Assignment not found", status=404)