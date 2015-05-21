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
            "approved_by_trainer" :{"$nin": [username]},
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

{u'Korean': [u'75653'], u'Chinese': [u'72287', u'76851', u'38911', u'74541', u'66713', u'71913', u'71059', u'70029', u'64265', u'74101', u'75449', u'71274', u'79960', u'73498', u'80229', u'69917', u'66109', u'3028', u'69984', u'64309', u'64758', u'70131', u'70377', u'60176', u'71414', u'75272', u'68660', u'71099', u'52951', u'58898', u'73039', u'74845', u'70778', u'79021', u'71519', u'77748', u'80237', u'68924', u'62171', u'71677', u'71022', u'72894', u'70727', u'69052', u'79963', u'29602', u'30857', u'46911', u'60438', u'71064', u'65010', u'62335', u'75342', u'73578', u'79753', u'73027', u'69210', u'80415', u'72288', u'75653', u'73926', u'74661', u'79540', u'71093', u'73185', u'81443', u'75297', u'31687', u'75328', u'70681', u'79779', u'69384', u'75209', u'65142', u'72905', u'71028', u'68291', u'68964', u'75511']}
