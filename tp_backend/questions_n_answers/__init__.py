import pymongo
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId

client = MongoClient("localhost",27017)
#client.noisy_NER.authenticate("fwadmin", "fwadmin")
db = client['noisy_NER']
entity_collection = db['entity']
questions = db['questions']

import os
import TP_Frontend_Backend_Bridge


def getNextQuestion(username):
    replyDict = {}
    mostImportantSurfaceTextQuestion = getNextHighestPriorityConcept(username, 'surface_text')
    mostImportantEntity_URLQuestion = getNextHighestPriorityConcept(username, 'entity_url')
    print mostImportantEntity_URLQuestion
    if mostImportantEntity_URLQuestion[1] > mostImportantSurfaceTextQuestion[1]:
        nextQuestion = (mostImportantEntity_URLQuestion[0],mostImportantEntity_URLQuestion[1],'entity_url')
    else:
        tmpAnswerList = getQuestion(mostImportantSurfaceTextQuestion[0], 'surface_text')
        if len(tmpAnswerList) > 1:
            if not any(dict1['intended_trainer'] == 'commonsense_linguist' for dict1 in tmpAnswerList): #see if any of the suggestion answer is intended for commonsense_linguist
                #no suggestion answer is intended for commonsense_linguist. it is safe to return this 'keyword question' in tp_frontend
                nextQuestion = (mostImportantSurfaceTextQuestion[0],mostImportantSurfaceTextQuestion[1],'surface_text')
            else:
                #one of the suggestion answer is intended for commonsense_linguist. we cannot return this 'keyword question'. infact we need to SKIP this entire keyword question on behalf of user
                answerObjectIDs = []
                for suggestion in tmpAnswerList:
                    answerObjectIDs.append(suggestion['_id'])
                skipQuestion(answerObjectIDs, username)
                #after current question has been skipped, return the NEXT question
                return getNextQuestion(username)
        else:
            nextQuestion = (mostImportantEntity_URLQuestion[0],mostImportantEntity_URLQuestion[1],'entity_url')
    
    answerList = getQuestion(nextQuestion[0], nextQuestion[2])
    replyDict['question'] = nextQuestion
    replyDict['suggestions'] = answerList
    return replyDict
        
    
def getNextHighestPriorityConcept(username,conceptType):
    mongoReply = entity_collection.aggregate([
        { "$match":{"intended_trainer":TP_Frontend_Backend_Bridge.projectName + "_trainer",
            "approved_by_trainer" :{"$nin": [username], "$exists":"true"},
            "skipped_by_trainer" :{"$nin": [username]},
            "disapproved_by_trainer" :{"$nin": [username]} }
         },                 
        {
            "$unwind": "$mentioned_in"
        },
        {"$group":
         {      "_id": "$" + conceptType,
                "freq": {
                    "$sum": 1
                }
            }
        },
        {"$sort" :{"freq":-1}},
        {"$limit":1}])
    entity_url =  mongoReply['result'][0]['_id'] #we are extracting data from 'result' key, then 0th element, then '_id' key because resopnse from mongodb contains nested json. try the above query in robomongo to know more
    frequency = mongoReply['result'][0]['freq']
    return ((entity_url,frequency)) #this returns a TUPLE. first element is entity_url, and 2nd element is sum of all mentioned_in

def getQuestion(question,conceptType):
    if conceptType == 'entity_url': mongo_query = { "entity_url": question}
    if conceptType == 'surface_text': mongo_query = { "surface_text": question}
    mongo_filter = { "mentioned_in": {"$slice": 5}}
    mongoCursor = entity_collection.find(mongo_query,mongo_filter)
    mongoReply = []
    for doc in mongoCursor:
        mongoReply.append(doc)
    return mongoReply


def skipQuestion(synonyms, user_id):
    """
    Add user id in skipped_by_trainee
    """
    if not synonyms or not user_id:
        return False
 
    for id in synonyms:
        mongoReply = entity_collection.find_one({"_id":id})
        if 'skipped_by_trainer' in mongoReply:
            if user_id not in mongoReply['skipped_by_trainer']:
                entity_collection.update(
                    {"_id":id},
                    {"$addToSet": {"skipped_by_trainer":user_id}
                })
        else:
            entity_collection.update(
                {"_id":id},
                {"$set":{"skipped_by_trainer":[user_id]}}
            )
        if 'approved_by_trainer' in mongoReply and user_id in mongoReply['approved_by_trainer']:
            entity_collection.update({"_id":id}, {"$pull": {"approved_by_trainer":user_id}})

        if 'disapproved_by_trainer' in mongoReply and user_id in mongoReply['disapproved_by_trainer']:
            entity_collection.update({"_id":id}, {"$pull": {"disapproved_by_trainer":user_id}})
    return True

def get_total_questions_count():
    """
    """
    return get_total_keyword_questions_count() + get_total_concept_questions_count()

def get_total_keyword_questions_count():
    """
    Get total or maximum number of questions to be asked
    """
    surface_text_count = get_question_count("surface_text")
    return surface_text_count

def get_total_concept_questions_count():
    """
    Get total or maximum number of questions to be asked
    """
    entity_count = get_question_count("entity_url")
    return entity_count

def get_question_count(concept_type):
    """
    mongo query to get count of questions
    """
    mongoReply = entity_collection.aggregate([
        { "$match":{"intended_trainer":TP_Frontend_Backend_Bridge.projectName+"_trainer"}
         },
        {
            "$unwind": "$mentioned_in"
        },
        {"$group":
         {      "_id": "$" + concept_type,
                "freq": {
                    "$sum": 1
                }
            }
        },
        {"$sort" :{"freq":-1}},
        {"$group":{"_id":"_id", "count": {"$sum": 1}}}
    ])
    if mongoReply['result']:
        return int(mongoReply['result'][0]['count'])
    return 0

def get_user_answered_count(id):
    """
    Get count of answered question by a specific user.
    """
    mongoReply = questions.find({"trainers":{"$in": [id]}})
    return len(list(mongoReply))
