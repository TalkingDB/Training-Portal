from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
import questions_n_answers as questions

@csrf_exempt
@login_required
def progress(request):

    total_questions = questions.get_total_questions_count()
    if request.method == 'POST':
        trainers = request.POST.getlist('checked[]')
        return_dict =  {'total-progress': get_progress(total_questions, trainers)['total']}
        result = json.dumps(return_dict)
        return HttpResponse(result)
    users = User.objects.all()
    trainers = [user.id for user in users]
    progress = get_progress(total_questions, trainers)

    return render(request, 'review/progress.html', {'users' :users, "progress": progress})


def get_progress(total_count, trainers):
    """
    Calculate progress of list of trainers and total number of questions.
    """
    # dict to add key = trainers, value = progress in decimals
    progress_dict = {}

    total = 0
    for trainer in trainers:
        # get answered entities of a trainer
        answered_count = questions.get_user_answered_count(int(trainer))
        total = total+answered_count
        progress_dict[trainer] = calculate_percentage(answered_count, total_count)
    progress_dict['total'] = float(calculate_percentage(total, total_count*len(trainers)))
    
    return progress_dict



def calculate_percentage(answered, total):
    """
    Calculate percentage according to answered questions and total number of questions

    return type: decimal
    """

    try:
        percentage = (float(answered)/float(total)) * 100
    except:
        percentage = 0.00
    return format(percentage, '.2f')
