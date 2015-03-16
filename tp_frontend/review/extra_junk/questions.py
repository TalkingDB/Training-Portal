from pymongo.mongo_client import MongoClient
import entity_model as em

client = MongoClient("training.smarter.codes",27017)
#client.noisy_NER.authenticate("fwadmin", "fwadmin")
db = client['noisy_NER']
entity_collection = db['entity']
new_c = db['questions']

 
def getQuestions():
    replyDict = {}
    
    surface_text = getAnsweredQuestions('surface_text')['result']
    entity_url = getAnsweredQuestions('entity_url')['result']
    questions = surface_text + entity_url
    
    sorted(questions, key=lambda k: k['freq'])
    get_synonyms(questions)
#    return questions
    
def getAnsweredQuestions(conceptType):
    mongoReply = entity_collection.aggregate([
        {"$match":
            {"intended_trainer":"Foodweasel_trainer",
                "$or":[
                    {"approved_by_trainer": {"$exists": "true"}},
                    {"disapproved_by_trainer": {"$exists":"true"}},
                    {"skipped_by_trainer": {"$exists":"true"}},
                ]
            }
         },                 
        {
            "$unwind": "$mentioned_in"
        },
        {"$group":
        {      "_id": "$"+ conceptType,
               "freq": {
                   "$sum": 1
               }
            }
        },
        {"$sort" :{"freq":-1}}])
    
    return mongoReply #this retm urns a TUPLE. first element is entity_url, and 2nd element is sum of all mentioned_in

def get_synonyms(questions):
    """
    get sysnonyms of all questions
    """
    output = []

    for ques in questions:
        trainers = []
        if '>' in ques['_id']:
            concept = "entity_url"
        else:
            concept = "surface_text"

        mongoReply = entity_collection.find({
            concept:ques['_id'],
            "$and":[
                {"approved_by_trainer": {"$exists": 0}},
                {"disapproved_by_trainer": {"$exists":0}},
                {"skipped_by_trainer": {"$exists":0}},
            ]
        })
        print mongoReply.count()
        if mongoReply.count():
            print "false"+ques['_id']
        else:
            data = entity_collection.find({
                concept:ques['_id'],
                "$or":[
                    {"approved_by_trainer": {"$exists": "true"}},
                    {"disapproved_by_trainer": {"$exists":"true"}},
                    {"skipped_by_trainer": {"$exists":"true"}},
                ]
            })
            for d in data:
                if 'approved_by_trainer' in d:
                    trainers = trainers + d['approved_by_trainer']
                if 'disapproved_by_trainer' in d:
                    trainers = trainers + d['disapproved_by_trainer']
                if 'skipped_by_trainer' in d:
                    trainers = trainers + d['skipped_by_trainer']
            new_c.insert({
                'question': ques['_id'],
                'frequency': ques['freq'],
                'trainers' : list(set(trainers))
            })

getQuestions()