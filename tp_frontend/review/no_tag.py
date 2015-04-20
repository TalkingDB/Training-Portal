from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from ConfigParser import RawConfigParser
import entity_model as em
from pymongo import MongoClient
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os

config = RawConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
config.read(BASE_DIR+'/config.ini')

# mongo configurations
mongoUrl =  config.get('mongo', 'MONGO_URL')
mongoPort = 27017
mongoDb = "noisy_NER"

client = MongoClient(mongoUrl, mongoPort)
db = client[mongoDb]
entityModel = db['entity']
entityModel.ensure_index('frequency')

@login_required
def display_no_tag(request):
    """
    Display no tags with pagination
    """

    if request.user.is_staff or request.user.is_superuser:
        no_tags = list(entityModel.find({ "$query": {"entity_url": "~NoTag"}, "$orderby": { "frequency" : -1 } }))
        paginator = Paginator(no_tags, 20) # Show 20  per page
        page = request.GET.get('page') # get current page number

        try:
            no_tags_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            no_tags_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            no_tags_list = paginator.page(paginator.num_pages)



        return render(request, 'review/no_tag.html', {"no_tags":no_tags_list})

    raise Http404