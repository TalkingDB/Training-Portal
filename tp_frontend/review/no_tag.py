from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from ConfigParser import RawConfigParser
import entity_model as em
from pymongo import MongoClient
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from search import get_search_question
from django.contrib import messages
import os
import json

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

@csrf_exempt
@login_required
def get_associated_entities(request):
    """
    Get all entities matching search text to associate  a No Tag with Entity
    """
    text = request.GET.get('data', '').replace(" ", "[-_\s]")
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    result = get_search_question(text,"entity_url")
    return HttpResponse(json.dumps(result))

@csrf_exempt
@login_required
def associate_entity(request):
    """
    Associate  a No Tag with Entity
    """
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404

    surface_text =  request.POST["surface_text"]
    entity =  request.POST["entity"]
    new = request.POST["new"]
    if new == "true":
        entity = entity.strip().replace(" ", "_").capitalize()
        if list(entityModel.find({"entity_url": "DBPedia>"+entity})) or list(entityModel.find({"entity_url": "DBPedia>"+entity.title()})) \
            or list(entityModel.find({"entity_url": "SmarterCodes>"+entity})):
            url = "reload"
            messages.error(request,"Entity with name "+entity+ " already exist! Please select from list of search options!")
            return HttpResponse(json.dumps({"url": url}))
        else:
            entity = "SmarterCodes>" + entity
    try:
        entityModel.update({"surface_text": surface_text}, {"$set": {"entity_url": entity, "approved_by_trainer":[request.user.id]}})
        url = "/review/"+ entity
        messages.success(request,'Keyword '+ str(surface_text)+ ' associated with ' + str(entity))
    except:
        url = "reload"
        messages.error(request,"Error in associating no tag with entity. Please Try again")

    return HttpResponse(json.dumps({"url":url}))


