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
    text = request.GET.get('search', '').replace(" ", "[-_\s]")
    to_send['result_entity'] = get_search_question(text,"entity_url")
    to_send['result_text'] =get_search_question(text,"surface_text")
    return render(request, 'review/search.html', to_send)


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
               }
            }
        },
        {"$sort" :{"freq":-1}}])
    return mongoReply['result']