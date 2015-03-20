import json
# from pymongo.mongo_client import MongoClient
# import re
#
# client = MongoClient("localhost",27017)
# #client.noisy_NER.authenticate("fwadmin", "fwadmin")
# db = client['noisy_NER']
# entity_collection = db['entity']
# test = db['test']
# f = open("mongoDumpFromConceptDigger.txt", "a")
# data = entity_collection.find({"intended_trainer" : "commonsense_linguist"}, {"_id": 0, "skipped_by_trainer": 0, "frequency": 0, "mentioned_in": 0, "disapproved_by_trainer": 0, "approved_by_trainer": 0})
# for d in data:
#     test.insert(d)
#     f.write(str(d) + "\n")
#
# f.close()

# f = open("mongoDumpFromConceptDigger.txt", "r")
#
# linguist_data = []
# for data in f:
#     sub = re.search("u'surface_text':\su'(.*?)'", data).group(1)
#     linguist_data.append(sub)

f = open("", "wb")

val = json.dump()