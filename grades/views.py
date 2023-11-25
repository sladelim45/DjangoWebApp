from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied
from . import models

def is_student(user):
    return user.groups.filter(name="Students").exists()

def is_ta(user):
    return user.groups.filter(name="Teaching Assistants").exists() or user.is_superuser

# Create your views here.
@login_required
def assignments(request):
    all_assignments = models.Assignment.objects.order_by("deadline")
    return render(request, "assignments.html", {
        'assignments': all_assignments
    })

@login_required
def index(request, assignment_id):
    try:
        asgn = models.Assignment.objects.get(pk=assignment_id)

        if is_ta(request.user):
            total_submissions = asgn.submission_set.count()
            submissions_assigned_to_you = asgn.submission_set.filter(grader__username="ta1").count()
            total_students = models.Group.objects.get(name="Students").user_set.count()
            return render(request, "index.html", {
                'assignment': asgn,
                'total_submissions': total_submissions,
                'submissions_assigned_to_you': submissions_assigned_to_you,
                'total_students': total_students,
                'is_ta': is_ta(request.user),
            })
        else:
            submission_info = None
            is_due = None
            try:
                submission = models.Submission.objects.get(assignment=asgn, author=request.user)
                filename = submission.file.name
                if submission.score is not None:
                    submission_info = f'Your submission, <a href="{submission.file.url}">{filename}</a>, received {round(submission.score, 1)}/{round(asgn.points, 1)} ({round(submission.score/asgn.points*100, 1)}%)'
                    is_due = True
                elif timezone.now() > asgn.deadline:
                    submission_info = f'Your submission, <a href="{submission.file.url}">{filename}</a>, is being graded'
                    is_due = True
                else:
                    submission_info = f'Your current submission is  <a href="{submission.file.url}">{filename}</a>'
                    is_due = False
            except:
                if timezone.now() > asgn.deadline:
                    submission_info = 'You did not submit this assignment and received 0 points'
                    is_due = True
                else:
                    submission_info = 'No current submission'
                    is_due = False

            return render(request, "index.html", {
                'assignment': asgn,
                'is_ta': is_ta(request.user),
                'is_due': is_due,
                'submission_info': submission_info,
            })  
    except models.Assignment.DoesNotExist:
        raise Http404("Assignment not found")

@login_required
@user_passes_test(is_ta)
def submissions(request, assignment_id):
    try:
        asgn = models.Assignment.objects.get(pk=assignment_id)

        if is_ta(request.user):
            submissions = asgn.submission_set.filter(grader=request.user).order_by("author__username")
        else:
            submissions = asgn.submission_set.all().order_by("author__username")
            
        return render(request, "submissions.html", {
            'assignment': asgn,
            'submissions': submissions
        })
    except models.Assignment.DoesNotExist:
        raise Http404("Assignment not found")
    except models.Submission.DoesNotExist:
        raise Http404("Submission not found")

@login_required
def profile(request):

    if is_ta(request.user):
        assignments = models.Assignment.objects.order_by("deadline")
        assignments_and_counts = []

        for assignment in assignments:
            count = "Not due"
            if timezone.now() > assignment.deadline:
                count = f'{assignment.submission_set.filter(grader=request.user, score__isnull=False).count()}/{assignment.submission_set.filter(grader=request.user).count()}'
            assignments_and_counts.append({'assignment': assignment, 'count': count})

        return render(request, "profile.html", {
            'assignments_and_counts': assignments_and_counts,
            'is_ta': is_ta(request.user),
        })
    else:
        assignments = models.Assignment.objects.order_by("deadline")
        assignments_and_scores = []
        total_available = 0
        total_earned = 0

        for assignment in assignments:

            if timezone.now() > assignment.deadline:
                try:
                    submission = models.Submission.objects.get(assignment=assignment, author=request.user)
                    if submission.score is not None:
                        score = (submission.score  / assignment.points)
                        total_available += assignment.weight
                        total_earned += (score * assignment.weight)
                        assignments_and_scores.append({'assignment': assignment, 'score': f'{round(score * 100, 1)}%'})
                    else:
                        assignments_and_scores.append({'assignment': assignment, 'score': 'Ungraded'})
                except models.Submission.DoesNotExist:
                    assignments_and_scores.append({'assignment': assignment, 'score': 'Missing'})
                    total_available += assignment.weight
            else:
                assignments_and_scores.append({'assignment': assignment, 'score': 'Not Due'})

        final_grade = 100 if total_available == 0 else total_earned / total_available * 100

        return render(request, "profile.html", {
            'assignments_and_scores': assignments_and_scores,
            'is_ta': is_ta(request.user),
            'final_grade': f'{round(final_grade, 1)}%',
        })

def login_form(request):
    if request.method == 'POST':
        username = request.POST.get('username', "")
        password = request.POST.get('password', "")
        next_url = request.POST.get('next', '/profile/')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password', 'next': next_url})

    next_url = request.GET.get('next', '/profile/')
    return render(request, 'login.html', {'next': next_url})

def logout_form(request):
    logout(request)
    return redirect('/profile/login')

@require_POST
@login_required
@user_passes_test(is_ta)
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
    
@login_required
@user_passes_test(is_student)
@require_POST
def submit(request, assignment_id):
    try:
        asgn = models.Assignment.objects.get(pk=assignment_id)
        if timezone.now() > asgn.deadline:
            return HttpResponseBadRequest("Assignment is past due.")
        submitted_file = request.FILES.get('file')
        try:
            submission = models.Submission.objects.get(assignment=asgn, author=request.user)
            submission.file = submitted_file
        except:
            submission = models.Submission.objects.create(assignment=asgn, author=request.user, file=submitted_file, score=None, grader=pick_grader(asgn))
        submission.save()
        return redirect(f"/{asgn.id}/")
    except:
        raise Http404("Assignment not found")
    

def pick_grader(assignment):
    ta_group = models.Group.objects.get(name="Teaching Assistants")
    tas = ta_group.user_set.all()
    tas_annotated = tas.annotate(total_assigned=Count("graded_set", filter=Q(graded_set__assignment=assignment)))  
    tas_ordered = tas_annotated.order_by('total_assigned')
    grader = tas_ordered.first()
    return grader

@login_required
def show_upload(request, filename):
    try:
        submission = models.Submission.objects.get(file=filename)

        if not (request.user == submission.author or request.user == submission.grader or request.user.is_superuser):
            raise PermissionDenied
        
        with submission.file.open() as fd:
            response = HttpResponse(fd)
            response["Content-Disposition"] = \
                f'attachment; filename="{submission.file.name}"'
            return response

    except models.Submission.DoesNotExist:
        raise Http404("Submission not found")
    except PermissionDenied:
        raise PermissionDenied
    
# only is called when DEBUG is False in settings.py
def assignment_not_found(request, exception=None):
    return HttpResponse("Assignment not found", status=404)