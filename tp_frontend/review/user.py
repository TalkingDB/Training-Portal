from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from ConfigParser import RawConfigParser
import entity_model as em
from pymongo import MongoClient
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import questions_n_answers as question_list
from progress import get_progress
from retrain import retraining
import json

import os
from ConfigParser import RawConfigParser

# Read config file
config = RawConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
config.read(BASE_DIR+'/config.ini')

# mongo configurations
mongoUrl =  config.get('mongo', 'MONGO_URL')
mongoPort = 27017
mongoDb = "noisy_NER"

client = MongoClient(mongoUrl, mongoPort)
db = client[mongoDb]
questionModel = db['questions']

# root dit path
root_dir_path = os.path.expanduser("~/Smarter.Codes/src")

@login_required()
def home(request):
    """
    Render home page of user

    if user is staff or admin show questions answered with trainers and option to
    update those ans.
        Functionality of retrain button

    else render page without them

    """
    # add data to to_send dict for template variables
    to_send = {}

    # to get retraining progress: False from start but if progress.txt exist
    # then set variable as True
    to_send['retraining_progress'] = False

    if os.path.isfile(root_dir_path+'/progress.txt'):
        to_send['retraining_progress'] = True

    if request.user.is_staff:
        questions = list(questionModel.find({ "$query": {}, "$orderby": { "frequency" : -1 } })) # get all answered questions
        paginator = Paginator(questions, 20) # Show 20  per page
        page = request.GET.get('page') # get current page number

        try:
            to_send['questions'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            to_send['questions'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            to_send['questions'] = paginator.page(paginator.num_pages)

    # Progress of current user
    # pass total questions and list of ids of user
    progress = get_progress([request.user.id])
    to_send['progress'] = progress

    return render(request, 'review/profile.html', to_send)


@login_required()
@csrf_exempt
def retrain(request):
    """
    Call method retrain catalog
    """
    if request.method == "GET":
        raise Http404

    # check if progress.txt exist in root_dir_path
    if os.path.isfile(root_dir_path+'progress.txt'):
        # if yes return a dict with message
        return {'process': "Process already running."}
    else:
        # call retraining
        result = retraining()
    return HttpResponse(json.dumps(result))

@login_required()
@csrf_exempt
def check_retraining_progress(request):
    """
    Check if retraining is in progress by checking if file exist : progress.txt

    As it is a xhr request send httpResponse of "string" true or "false"
    """
    if os.path.isfile(root_dir_path+'/progress.txt'):
        return HttpResponse("true")

    return HttpResponse("false")

