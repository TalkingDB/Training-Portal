from pymongo import MongoClient
from ConfigParser import RawConfigParser
import os
from django.shortcuts import render

config = RawConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
config.read(BASE_DIR+'/config.ini')

client = MongoClient(config.get('mongo', 'MONGO_URL'),27017)
#client.noisy_NER.authenticate("fwadmin", "fwadmin")
db = client['noisy_NER']
entity_collection = db['entity']


def search(request):
    """
    """
    to_send = {}
    no_tag_list = []
    text_list = []
    text = request.GET.get('search', '').replace(" ", "[-_\s]")
    result_entity = get_search_question(text,"entity_url")
    for result in get_search_question(text,"surface_text"):
        if result["entity_url"] == "~NoTag":
            no_tag_list.append(result)
        else:
            text_list.append(result)
    return render(request, 'review/search.html', {
        "result_entity": result_entity,
        "result_text": text_list,
        "result_no_tag": no_tag_list
    })


def get_search_question(text,type):
    mongoReply = entity_collection.aggregate([
        {"$match":
            {type  : {"$regex":text, "$options": "i"}}
         },
        {"$group":
        {      "_id":"$"+type,
               "freq": {
                   "$sum": 1
               },
               "name": {
                   "$first": "$"+ type
               },
               "entity_url": {
                    "$first": "$entity_url"
               }
            }
        },
        {"$sort" :{"freq":-1}}])
    return mongoReply['result']