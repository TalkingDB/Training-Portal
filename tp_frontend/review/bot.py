from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from pymongo import MongoClient
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import os
import inflect
import TP_Frontend_Backend_Bridge as t

p = inflect.engine()
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
#   if a special character like SODA(32) it only matches soda 
    is_spcl_char_entity = False
    #process mongodata
    for entity in data['result']:

        if ">" in entity["_id"]:
            # get synonyms of specific entity
            synonyms = get_synonyms(entity["_id"])

            # Check if entity name contains "(" because we have some entities like DBPedia>Chicken_(food)
            # so in this case we will split this entity by ">" pick Chicken_(food) then split by "_(" and
            # pick Chicken, Convert it to lower case chicken and save its plural form (chickens)
            # we will check synonyms for chicken, chickens and chicken (food) (as default value)

            if "(" in entity["_id"]:
                # substring from entity_url "DBPedia>Chicken_(Food)" will become "chicken"
                synonym_substring = entity["_id"].split('>')[1].split("_(")[0].replace("_", " ").lower()

                # plural form of substring (chicken) will be chickens
                plural_synonym = p.plural(synonym_substring)
                # Set "is_spcl_char = True" so that we can know that this entity_url contains a special char
                # and we need different operation for it
                is_spcl_char_entity = True
            else:
                # If entity_url is normal text (DBPedia>Chicken). It will just split by ">", Pick Chicken and convert
                # to lower case (chicken)
                # replace("_", " ") will only work if we encounter entity url like (DBPedia>Diet_Coke)
                # In this case after split (Diet_coke) we will replace "_" by " " and convert to lower (diet coke)
                # In the end p.plural(chicken) will give us "chickens" and p.plura(diet coke) will give us "diet cokes"

                plural_synonym = p.plural(entity["_id"].split('>')[1].replace("_", " ").lower())

            # set a static variable "is_plural_synonym to False"
            # We will check this variable so we can know that plural_synonym exists in our list
            # of synonyms. If It is set to True that means synonym with same text exist else we have to add new text
            is_plural_synonym = False
            


            for synonym in synonyms:
                synonym_to_be_deleted = False
                # Condition 1: source of synonym should be article_categories_en.nt
                # It is because we observed suggestion names of article_categories_en.nt are same as question
                # DBPedia>Diet_coke : diet coke

                if 'how_this_record' in synonym and synonym['how_this_record'] == "article_categories_en.nt":
                    # Condition 1 true so Add user id to list of approved trainers
                    synonym_to_be_deleted = True
                    entityModel.update(
                        {"_id": synonym["_id"]},
                        {"$addToSet": {"approved_by_trainer":user.id}}
                    )

                # Condition 2: plural_synonym text already exist in our synonym list
                elif synonym['surface_text'] == plural_synonym:

                    # If this condition is true we will not add new synonym so change value of "is_plural_synonym" to True
                    is_plural_synonym = True
                    synonym_to_be_deleted = True
                    entityModel.update(
                        {"_id": synonym["_id"]},
                        {"$addToSet": {"approved_by_trainer":user.id}}
                    )

                # Condition 3 : Check if "is_spcl_char_entity" is True if yes than it will compare
                # current synonym's surface text with synonym_substring. If we are to find a match in our
                # synonym list check the value
                elif is_spcl_char_entity and synonym['surface_text'] == synonym_substring:
                    entityModel.update(
                        {"_id": synonym["_id"]},
                        {"$addToSet": {"approved_by_trainer":user.id}}
                    )

                # If every condition failed then add ROBOT to list of "disapproved_by_trainer" of specific synonym
                else:
                    entityModel.update(
                        {"_id": synonym["_id"]},
                        {"$addToSet": {"disapproved_by_trainer":user.id}}
                    )
                if synonym_to_be_deleted == True:
                    entityModel.remove({"surface_text":synonym['surface_text'],"entity_url":{"$not":{"$eq" : synonym['entity_url']}}})
                    
            # Add a new synonym if synonym matching test 0f plural_synonym dose not exist.
            if not is_plural_synonym:
                entityModel.insert({
                        'surface_text': plural_synonym,
                        'entity_url': entity["_id"],
                        'approved_by_trainer': [user.id],
                        'frequency': 0,
                        "how_this_record": 'user_defined',
                        "intended_trainer" : t.projectName+"_trainer",

                     })
            
                
                
            # enter questions in questions collection for progress and display of answered questions
            if questionModel.find({"question": entity["_id"]}).count():
                # if question exist add user id in list of trainers
                questionModel.update(
                    {"question": entity["_id"]},
                    {"$addToSet": {"trainers":user.id}}
                )
            else:
                # if question dosent exist insert in table
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
        {   "$match":{"intended_trainer":t.projectName+"_trainer"}
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

def get_synonyms(entity):
    """
    Get synonyms of entity
    """

    data = entityModel.find({
        "entity_url": entity,
        "intended_trainer" : t.projectName+"_trainer"
    }, {"mentioned_in": 0, "frequency": 0, "seed_category": 0})
    return data