from django.shortcuts import render, redirect
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

import os
from ConfigParser import RawConfigParser
config = RawConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
config.read(BASE_DIR+'/config.ini')
mongoUrl =  config.get('mongo', 'MONGO_URL')
mongoPort = 27017
mongoDb = "noisy_NER"

client = MongoClient(mongoUrl, mongoPort)
db = client[mongoDb]
questionModel = em.EntityModel(db, 'questions')



@login_required()
def home(request):
    """
    """
    to_send = {}
    if request.user.is_staff:
        questions = list(questionModel.select_all())
        paginator = Paginator(questions, 20) # Show 20  per page

        page = request.GET.get('page')
        try:
            to_send['questions'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            to_send['questions'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            to_send['questions'] = paginator.page(paginator.num_pages)
    total_questions = question_list.get_total_questions_count()
    progress = get_progress(total_questions, [request.user.id])
    to_send['progress'] = progress
    return render(request, 'review/profile.html', to_send)


@login_required()
@csrf_exempt
def retrain(request):
    """
    Call method retrain
    """
    if request.method == "GET":
        raise Http404
    retraining()
    return render(request, 'review/profile.html')
