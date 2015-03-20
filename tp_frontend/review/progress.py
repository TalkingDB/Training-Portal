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
    """
    Get progress of every user

    total No of questions : max no. of questions of concept + max no. of questions of keyword
    trainers = list of all users

    if ajax request so get list of checked trainers call for progress for that list of trainers.
    """
    # get keyword question
    keyword = questions.get_total_keyword_questions_count()
    #get concept type questions
    concept = questions.get_total_concept_questions_count()

    # request for updating total progress
    if request.method == 'POST':
        # get list of trainers checked from front end
        # django template will pass list of unicode values
        trainers = request.POST.getlist('checked[]')
        # pass values to get progress and convert list of unicode values to list of integers
        return_dict =  {'total-progress': get_progress(concept, keyword, [int(id) for id in trainers])['total']}
        result = json.dumps(return_dict)
        return HttpResponse(result)
    users = User.objects.all()
    trainers = [user.id for user in users]
    # get progress of every user
    progress = get_progress(concept, keyword, trainers)

    return render(request, 'review/progress.html', {'users' :users, "progress": progress})


def get_progress(concept, keyword, trainers):
    """
    Calculate progress of list of trainers and total number of questions.
    """


    # check if bot user exist
    if User.objects.get(username='robot'):
        # get object
        robo_trainer = User.objects.get(username='robot')
        # check if user id in trainers list
        if robo_trainer.id in trainers:
            # replace id of list by user object
            # trainers.index(robo_trainer.id) will give index of bot id
            trainers[trainers.index(robo_trainer.id)] = robo_trainer

    # dict to add key = trainers, value = progress in decimals
    progress_dict = {}
    total_count = concept+keyword
    total = 0
    for trainer in trainers:
        # if type of trainer is object and object is of User class
        if type(trainer) is User:
            # replace trainer object by trainer id
            trainer = trainer.id
            # total no of questions will be equal to no of concept questions
            total_count = concept

        # get answered entities of a trainer
        answered_count = questions.get_user_answered_count(trainer)
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
