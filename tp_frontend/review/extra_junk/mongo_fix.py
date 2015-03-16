
from pymongo.mongo_client import MongoClient

client = MongoClient("localhost",27017)
#client.noisy_NER.authenticate("fwadmin", "fwadmin")
db = client['noisy_NER']
entity_collection = db['questions']
synonym_collection = db['entity']


def correct():

    #users = [u'NumberLong(1)',u'NumberLong(2)',u'NumberLong(3)',u'NumberLong(4)',u'NumberLong(5)',u'NumberLong(6)',u'NumberLong(7)',u'NumberLong(8)',u'NumberLong(9)',u'NumberLong(10)',u'NumberLong(11)']
    users = [1,2,3,4,5,6,7,8,9,10,11]
    for user in users:
        print user
        questions = entity_collection.find({"trainers": {"$in": [user]}})
        print questions
        for question in questions:

            type = "surface_text"
            find = "entity_url"
            if '>' in question:
                type = "entity_url"
                find = "surface_text"

            synonyms = synonym_collection.find({
             type: question['question'], "skipped_by_trainer":{"$in": [user]}
            }, {"mentioned_in": 0, "how_this_record": 0, "seed_category":0, "frequency": 0, "intended_trainer":0})
            synonyms1 = synonym_collection.find({
             type: question['question'], "skipped_by_trainer":{"$nin": [user]}
            }, {"mentioned_in": 0, "how_this_record": 0, "seed_category":0, "frequency": 0, "intended_trainer":0})
            if synonyms.count():
                if synonyms1.count():
                    for synonym in synonyms:
                        print synonym
                        synonym_collection.update({"_id":synonym['_id']}, {"$pull": {"skipped_by_trainer":long(user)}})
                        synonym_collection.update({"_id":synonym['_id']}, {"$addToSet": {"disapproved_by_trainer":long(user)}})


correct()