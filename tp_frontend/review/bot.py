from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from pymongo import MongoClient
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
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
entityModel = db['entity']
questionModel = db['questions']

# root dit path
root_dir_path = os.path.expanduser("~/Smarter.Codes/src")


@login_required()
@csrf_exempt
def start_training(request):
    """
    Start Bot Training

    If Bot with username ROBOT is present in database start training
    Else Make a new user named ROBOT and then start training

    For Training Run mongo query to get all questions not answered by bot user.

    After getting valid list of questions add bot user id to set of approved_by_trainers or disapproved_by_trainers
    """
    # Check if request is post or requesting user is of staff or admin group
    if request.method == "GET" or not request.user.is_staff or not request.user.is_superuser:
        return Http404

    # Create user if dosent exist
    # get_or_create is a built in django orm method - get user or create new user
    user, created = User.objects.get_or_create(username="robot")
    if created:
        user = User.objects.get(username="robot")

    #Get data from mongodb
    data = mongoquery(user.id, "entity_url")

    #process mongodata
    for entity in data['result']:
        # get synonyms of specific entity
        synonyms = get_synonyms(entity["_id"])
        for synonym in synonyms:
            # Condition 1: source of synonym should be article_categories_en.nt
            # It is because we observed suggestion names of article_categories_en.nt are same as question
            # DBPedia>Diet_coke : diet coke

            if 'how_this_record' in synonym and synonym['how_this_record'] == "article_categories_en.nt":
                # Condition 1 true so Add user id to list of approved trainers
                print "adding synonym approved" + synonym["surface_text"] + entity["_id"]
                entityModel.update(
                    {"_id": synonym["_id"]},
                    {"$addToSet": {"approved_by_trainer":user.id}}
                )
            else:
                # Condition 1 false so Add to user id to list of disapproved by trainers
                entityModel.update(
                    {"_id": synonym["_id"]},
                    {"$addToSet": {"disapproved_by_trainer":user.id}}
                )

        # enter questions in questions collection for progress and display of answered questions
        if questionModel.find({"question": entity["_id"]}).count():
            # if question exist add user id in list of trainers
            print "updating question" + str(entity["_id"])
            questionModel.update(
                {"question": entity["_id"]},
                {"$addToSet": {"trainers":user.id}}
            )
        else:
            # if question dosent exist insert in table
            print "Making a new question "+ entity["_id"]
            ques = {
                'question': entity["_id"],
                'frequency': entity["freq"],
                'trainers': [user.id]
            }
            questionModel.insert(ques)

    return HttpResponse({"process": "finished"})


def mongoquery(user_id, conceptType):
    """
    mongo query to get list of entities
    """
    mongodata = entityModel.aggregate([
        {   "$match":{"intended_trainer":"Foodweasel_trainer",
            "approved_by_trainer" :{"$nin": [user_id]},
            "skipped_by_trainer" :{"$nin": [user_id]},
            "disapproved_by_trainer" :{"$nin": [user_id]},
            }
        },
        {
            "$unwind": "$mentioned_in"
        },
        {"$group":
            {   "_id": "$" + conceptType,
                "freq": {
                    "$sum": 1
                },
            }
         },

         {"$sort" :{"freq":1}}
    ])

    return mongodata

def get_synonyms(entity, source="article_categories_en.nt"):
    """
    Get synonyms of entity
    """

    data = entityModel.find({
        "entity_url": entity,
        "intended_trainer" : "Foodweasel_trainer"
    }, {"mentioned_in": 0, "frequency": 0, "seed_category": 0})
    return data