from django.shortcuts import render, redirect, HttpResponse
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import entity_model as em
from pymongo import MongoClient
from bson.objectid import ObjectId
import questions_n_answers as questions
from django.conf import settings
from collections  import OrderedDict
import os
import json
from progress import get_progress
from ConfigParser import RawConfigParser

config = RawConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
config.read(BASE_DIR+'/config.ini')

mongoUrl =  config.get('mongo', 'MONGO_URL')
mongoPort = 27017
mongoDb = "noisy_NER"
collection = 'entity'

client = MongoClient(mongoUrl, mongoPort)
db = client[mongoDb]
questionModel = em.EntityModel(db, 'questions')
entity_collection = db['entity']

file_path = os.path.expanduser("~/Smarter.Codes/customer_files/foodweasel.com/Training_Portal/")

@login_required()
def index(request, resource=None):

    user_id = request.user.id
    if resource:
        if '>' in resource:
            entity_type = 'entity_url'
        else:
            entity_type = 'surface_text'
        ques = (resource, 'None', entity_type)
        entities = questions.getQuestion(ques[0], ques[2])
    else:
        ques_list = questions.getNextQuestion(request.user.id)
        ques = ques_list['question']
        entities = ques_list['suggestions']
    if entities and entities[0]["entity_url"] == "~NoTag":
        progress = get_progress([request.user.id])
        mentioned_in=[]
        # for mentioned in entities[0]["mentioned_in"]:
        #     string_val = mentioned.split('.')
        #if len(mentioned_in) < 10:

        # TODO: Remove Code and Use "mentioned_in"
        if os.path.isfile(file_path+"1"):
            f = open(file_path+"1", "r")
            lines = f.read().split("\n")
            for line in lines:
                if len(mentioned_in) == 10:
                    break
                if entities[0]["surface_text"].replace("_", " ") in line.decode('utf-8'):
                    if line not in mentioned_in:
                        mentioned_in.append(line)
        if os.path.isfile(file_path+"2"):
            f = open(file_path+"2", "r")
            lines = f.read().split("\n")
            for line in lines:
                if len(mentioned_in) == 10:
                    break
                if entities[0]["surface_text"].replace("_", " ") in line.decode('utf-8'):
                    if line not in mentioned_in:
                        mentioned_in.append(line)
        to_send = {
            'no_tag':'True',
            "progress":progress,
            "text": entities[0]["surface_text"],
            "frequency": entities[0]["frequency"],
            "mentioned_in": mentioned_in,
        }
        return render(request, 'review/index.html', to_send)
    if entities:
        if ques[2] == 'entity_url':
            entity_text = entities[0]['entity_url'].split('>')[1]
            synonym_type = 'surface_text'
        else:
            entity_text = ques[0]
            synonym_type = 'entity_url'
        entity_synonyms = {}
        total_frequency = 0
        skipped_by = []
        for entity in entities:
            trainers = []
            checked = False
            if 'approved_by_trainer' in entity:
                trainers = entity['approved_by_trainer']
                if request.user.id in entity['approved_by_trainer']:
                    checked = True
            if 'skipped_by_trainer' in entity:
                skipped_by = skipped_by + entity['skipped_by_trainer']
            if '>' in entity[synonym_type]:
                surface_text = entity[synonym_type].split('>')[1]
                val = surface_text.replace("_", " ").replace("-", " ")
            else:
                val = entity[synonym_type]
            if 'frequency' in entity:
                frequency = int(entity['frequency'])
            else:
                frequency = 0
            entity_synonyms[val] = {
                'frequency':frequency,
                'checked':checked,
                'id': entity['_id'],
                'trainers': trainers,
             #   'source': entity.how_this_record
            }

            total_frequency += frequency
        synonyms = sorted(entity_synonyms.items(),key=lambda x: x[1]['frequency'],reverse=True)
        #sorted_dict = {[synonym] for synonym in synonyms}
        sorted_list = []
        for synonym in synonyms:
            sorted_list.append({synonym[0]:synonym[1]})

        progress = get_progress([request.user.id])
        return render(request, 'review/index.html', {
                'entity': entity_text,
                'text': (' ').join(entity_text.split('_')),
                'synonyms': sorted_list,
                'frequency':total_frequency,
                'concept_type': ques[2],
                'question': ques[0],'skipped_by': list(set(skipped_by)),
                'progress': progress
        })
    else:
        return render(request, 'review/index.html', {'error':'Resource Not Found!'})

# TODO: Remove save code for surface text and merger entity and surface
@csrf_exempt
@login_required()
def save(request, entity):

    entity_url = "DBPedia>"+entity
    entityModel = em.EntityModel(db, collection)
    if request.method == "GET" or not entity:
        raise Http404
    checked = request.POST.getlist('checked[]')
    unchecked = request.POST.getlist('unchecked[]')
    user_defined = request.POST.getlist('user_defined[]')
    question = request.POST.getlist('question[]')
    if checked:
        for id in checked:
            entity = entityModel.select_one({"_id":ObjectId(id)})
            if 'skipped_by_trainer' in entity and \
                request.user.id in entity['skipped_by_trainer']:
                    entityModel.update({"_id":ObjectId(id)}, {"$pull": {"skipped_by_trainer":request.user.id}})
            if 'disapproved_by_trainer' in entity and \
                request.user.id in entity['disapproved_by_trainer']:
                    entityModel.update({"_id":ObjectId(id)}, {"$pull": {"disapproved_by_trainer":request.user.id}})
            if 'approved_by_trainer' in entity:
                entityModel.update({"_id":ObjectId(id)}, {"$addToSet": {"approved_by_trainer":request.user.id}})
            else:
                entityModel.update({"_id":ObjectId(id)}, {"$set":{"approved_by_trainer":[request.user.id]}})

    if unchecked:
        for id in unchecked:
            entity = entityModel.select_one({"_id":ObjectId(id)})
            if 'skipped_by_trainer' in entity and \
                request.user.id in entity['skipped_by_trainer']:
                    entityModel.update({"_id":ObjectId(id)}, {"$pull": {"skipped_by_trainer":request.user.id}})
            if 'approved_by_trainer' in entity and \
                request.user.id in entity['approved_by_trainer']:
                entityModel.update({"_id":ObjectId(id)}, {"$pull": {"approved_by_trainer":request.user.id}})
            if 'disapproved_by_trainer' in entity:
                entityModel.update({"_id":ObjectId(id)}, {"$addToSet": {"disapproved_by_trainer":request.user.id}})
            else:
                entityModel.update({"_id":ObjectId(id)}, {"$set":{"disapproved_by_trainer":[request.user.id]}})

    if user_defined:
        docs= []
        for value in user_defined:
            #entity = entityModel.select_by({'entity_url':'~NoTag', "surface_text":value})
            frequency = 0
            # if entity:
            #     frequency = entity[0]['frequency']
            surface_text = value.strip().lower()
            if surface_text:
                no_tags = list(entity_collection.find({"entity_url": "~NoTag", "surface_text": surface_text}))
                if no_tags:
                    for tag in no_tags:
                        print tag["_id"]
                        entity_collection.update(
                            {"_id": tag["_id"]},
                            {"$set": { 'entity_url': entity_url, "approved_by_trainer": [request.user.id]}}
                        )
                else:
                    docs.append({
                        'surface_text': surface_text,
                        'entity_url':entity_url,
                        'approved_by_trainer': [request.user.id],
                        'frequency': frequency,
                        "how_this_record": 'user_defined',
                        "intended_trainer" : "Foodweasel_trainer",

                     })
        if docs:
            entityModel.insert_many(docs)
    if question:
        question[0] = question[0].replace('&gt;', '>')
        ques = questionModel.select_one({'question' : question[0]})
        if ques:
            questionModel.update({"_id":ques['_id']}, {"$addToSet": {"trainers": request.user.id}})
        else:
            ques = {
                'question': question[0],
                'frequency': int(question[1]),
                'trainers': [request.user.id]
            }
            questionModel.insertQuestion(ques)

    return redirect('/review')

@csrf_exempt
@login_required()
def save_surface_text(request, entity):

    surface_text = entity
    entityModel = em.EntityModel(db, collection)
    trainers = []
    if request.method == "GET" or not entity:
        raise Http404
    checked = request.POST.getlist('checked[]')
    unchecked = request.POST.getlist('unchecked[]')
    question = request.POST.getlist('question[]')
    if checked:
        for id in checked:
            entity = entityModel.select_one({"_id":ObjectId(id)})
            if 'skipped_by_trainer' in entity and \
                request.user.id in entity['skipped_by_trainer']:
                    entityModel.update({"_id":ObjectId(id)}, {"$pull": {"skipped_by_trainer":request.user.id}})
            if 'disapproved_by_trainer' in entity and \
                request.user.id in entity['disapproved_by_trainer']:
                    entityModel.update({"_id":ObjectId(id)}, {"$pull": {"disapproved_by_trainer":request.user.id}})
            if 'approved_by_trainer' in entity:
                entityModel.update({"_id":ObjectId(id)}, {"$addToSet": {"approved_by_trainer":request.user.id}})
            else:
                entityModel.update({"_id":ObjectId(id)}, {"$set":{"approved_by_trainer":[request.user.id]}})

    if unchecked:
        for id in unchecked:
            entity = entityModel.select_one({"_id":ObjectId(id)})
            if 'skipped_by_trainer' in entity and \
                request.user.id in entity['skipped_by_trainer']:
                    entityModel.update({"_id":ObjectId(id)}, {"$pull": {"skipped_by_trainer":request.user.id}})
            if 'approved_by_trainer' in entity and \
                request.user.id in entity['approved_by_trainer']:
                entityModel.update({"_id":ObjectId(id)}, {"$pull": {"approved_by_trainer":request.user.id}})
            if 'disapproved_by_trainer' in entity:
                entityModel.update({"_id":ObjectId(id)}, {"$addToSet": {"disapproved_by_trainer":request.user.id}})
            else:
                entityModel.update({"_id":ObjectId(id)}, {"$set":{"disapproved_by_trainer":[request.user.id]}})


    if question:
        ques = questionModel.select_one({'question' : question[0]})
        if ques:
            questionModel.update({"_id":ques['_id']}, {"$addToSet": {"trainers": request.user.id}})
        else:
            ques = {
                'question': question[0],
                'frequency': int(question[1]),
                'trainers': [request.user.id]
            }
            questionModel.insertQuestion(ques)

    return redirect('/review')


@csrf_exempt
@login_required
def skip(request):

    if request.method == "GET":
        raise Http404

    synonyms = request.POST.getlist('synonyms[]')
    question = request.POST.getlist('question[]')
    skipped = questions.skipQuestion([ObjectId(id) for id in synonyms], request.user.id)

    if '&gt;' in question[0]:
        question[0] = question[0].replace('&gt;', '>')
    ques = questionModel.select_one({'question': str(question[0])})

    if ques:
        questionModel.update({"_id":ques['_id']}, {"$addToSet": {"trainers":request.user.id}})
    else:
        ques = {
            'question': question[0],
            'frequency': int(question[1]),
            'trainers': [request.user.id]
        }
        questionModel.insertQuestion(ques)
    if request.is_ajax():
        result = json.dumps({"status": "200"})
        return HttpResponse(result)
    return redirect('/review')


def delete(request, id):
    entity = Entity.objects.get(id=id)
    
    if entity:
        entity.is_deleted = True
        entity.save()
        
    return redirect('/review')

@csrf_exempt
@login_required
def get_details_by_id(request, query_string, entity_id):
    """
    This method will receive id of entity and query string.
    if query_string and entity corresponding to id exists,
    Return that specific query data

    if query string is equal to full data . Return object of that entity
    """
    entityModel = em.EntityModel(db, collection)
    entity = entityModel.select_one({"_id":ObjectId(entity_id)})
    if entity and entity[query_string]:
        return HttpResponse(entity[query_string].replace('_', ' '))
    return HttpResponse("Not able to find source")
