from pymongo.mongo_client import MongoClient
from communicate_outside import MongoCLI
from communicate_outside import shell
from communicate_outside import socket_sender
import config
import json
import networkx
import os
import sys
import time
sys.path.append(os.getcwd() + "/../")
import TP_Frontend_Backend_Bridge
import re

client = MongoClient("localhost", 27017)
db = client['noisy_NER']
synonym_collection = db['entity']

def filter_CommonSense_mongoDumpFromConceptDigger(synonym_collection):
    # Open file containing data of commonsense linguist and add surface text to a list
    with open("data/mongoDumpOfCommonSenseTraining.txt", "r") as f:
        linguist_data = re.findall('"surface_text"\s:\s"(.*?)"', f.read())

    # replace lines having same surface text as commonsense linguist
    for data in linguist_data:
        synonym_collection.remove({"surface_text":data})

def dropTables():
    MongoCLI.mongo_collection_drop("noisy_NER", "entity")
    MongoCLI.mongo_collection_drop("noisy_NER", "Entity_to_Command")

def insertVariableIntoMongoDb(variable):
    f = open("data/mongoDumpFromConceptDigger.txt", "wb")
    f.write(variable)
    """
    Forward entities, their surface_text to Noisy NER
    """
    import os
    MongoCLI.mongo_import("noisy_NER", "entity", os.getcwd() + "/data/mongoDumpFromConceptDigger.txt")
    f.close()

"""
Read Seed Categories from TP Frontend
"""
#TODO: Change these lines
#seedCategories = '[["Category:Ceremonial_food_and_drink",5,0,1],["Category:Cuisine",5,0,1],["Category:Food_and_drink",0,0,1],["Category:Food_and_drink_by_country",5,0,1],["Category:Food_and_drink_preparation",5,0,1],["Category:Appetizers",4,0,1],["Category:Breads",4,0,1],["Category:Chocolate",4,0,1],["Category:Condiments",4,0,1],["Category:Convenience_foods",4,0,1],["Category:Dairy_products",4,0,1],["Category:Desserts",4,0,1],["Category:Dips_(food)",4,0,1],["Category:Dishes_by_main_ingredient",4,0,1],["Category:Dried_foods",4,0,1],["Category:Dumplings",4,0,1],["Category:Edible_fungi",4,0,1],["Category:Edible_nuts_and_seeds",4,0,1],["Category:Edible_plants",4,0,1],["Category:Eggs_(food)",4,0,1],["Category:Fast_food",4,0,1],["Category:Fermented_foods",4,0,1],["Category:Food_ingredients",4,0,1],["Category:Food_portal",4,0,1],["Category:Food_products",4,0,1],["Category:Food_templates",4,0,1],["Category:Foods_by_cooking_technique",4,0,1],["Category:Fruit",4,0,1],["Category:Holiday_foods",4,0,1],["Category:Imitation_foods",4,0,1],["Category:Kosher_food",4,0,1],["Category:Lists_of_foods",4,0,1],["Category:Meat",4,0,1],["Category:Meat_substitutes",4,0,1],["Category:Military_food",4,0,1],["Category:Noodles",4,0,1],["Category:Pancakes",4,0,1],["Category:Pasta",4,0,1],["Category:Pastries",4,0,1],["Category:Patented_foods",4,0,1],["Category:Pies",4,0,1],["Category:Porridges",4,0,1],["Category:Puddings",4,0,1],["Category:Salads",4,0,1],["Category:Sandwiches",4,0,1],["Category:Sauces",4,0,1],["Category:Seafood",4,0,1],["Category:Snack_foods",4,0,1],["Category:Soups",4,0,1],["Category:Spreads_(food)",4,0,1],["Category:Staple_foods",4,0,1],["Category:Stews",4,0,1],["Category:Vegetables",4,0,1],["Category:Wedding_food",4,0,1],["Category:Beverages_by_country",4,0,1],["Category:Lists_of_beverages",4,0,1],["Category:Alcoholic_beverages",4,0,1],["Category:Non-alcoholic_beverages",4,0,1],["Category:Barley-based_beverages",4,0,1],["Category:Brand_name_beverage_products",4,0,1],["Category:Beverage_companies",4,0,1],["Category:Caffeinated_beverages",4,0,1],["Category:Chocolate_beverages",4,0,1],["Category:Cold_beverages",4,0,1],["Category:Hot_beverages",4,0,1],["Category:Maize_beverages",4,0,1],["Category:Mixed_drinks",4,0,1],["Category:Rice_drinks",4,0,1],["Category:Drink_stubs",4,0,1],["Category:Beverages",0,0,1]]' 
#seedCategories = '[["Category:Ceremonial_food_and_drink",1,0,1]]'
allCommonNounSeedCategories = '[["Category:Clothing",5,0,1]]'
allAttributiveSeedCategories = '[["Category:Sizes_in_clothing",5,0,1],["Category:Color", 5,0,1]]'
allProperNounSeedCategories = '[["Category:Fashion_by_nationality", 4,0,1],["Category:Clothing_companies", 3,0,1]]'
"""
Intialize an empty variable mongoDumpFromConceptDigger
Get All Entities which belongs to allNounSeedCategories
mongoDumpFromConceptDigger= all categories from allNounSeedCategories

Forward seedCategories to 'Concept Digger & Synonms Finder' component
"""
mongoDumpFromConceptDigger = ""
dropTables()
t1 = time.time()

CommonNounMongoDumpFromConceptDigger = socket_sender.sendPacketOverSocket(config.conceptDiggerHostAddress, config.conceptDiggerPort, allCommonNounSeedCategories)
CommonNounMongoDumpFromConceptDigger = re.sub('}', ',"intended_trainer":"' + TP_Frontend_Backend_Bridge.projectName + '_trainer","entity_part_of_speech":"common"}', CommonNounMongoDumpFromConceptDigger)
insertVariableIntoMongoDb(CommonNounMongoDumpFromConceptDigger) #insert commonnounmongodump

allAttributiveMongoDumpFromConceptDigger = socket_sender.sendPacketOverSocket(config.conceptDiggerHostAddress, config.conceptDiggerPort, allAttributiveSeedCategories)
allAttributiveMongoDumpFromConceptDigger = re.sub('}', ',"intended_trainer":"' + TP_Frontend_Backend_Bridge.projectName + '_trainer" ,"entity_part_of_speech":"attributive"}', allAttributiveMongoDumpFromConceptDigger)
allAttributive = re.findall('"entity_url"\s:\s"(.*?)"', allAttributiveMongoDumpFromConceptDigger)
#print allAttributive
for attributive_entity_url in allAttributive:
    if ">" in attributive_entity_url:
        #    if "(" in attributive_surface_text:
        #            attributive_surface_text = attributive_surface_text.replace("(","")
        #    if ")" in attributive_surface_text:
        #            attributive_surface_text = attributive_surface_text.replace(")","")
        synonym_collection.remove({"entity_url":attributive_entity_url})
    else:
        print attributive_entity_url


#CommonNounAndAttributiveDump = OnlyCommonNounDump + allAttributiveMongoDumpFromConceptDigger
insertVariableIntoMongoDb(allAttributiveMongoDumpFromConceptDigger) #insert all attributive to mongo



properNounMongoDumpFromConceptDigger = socket_sender.sendPacketOverSocket(config.conceptDiggerHostAddress, config.conceptDiggerPort, allProperNounSeedCategories)
properNounMongoDumpFromConceptDigger = re.sub('}', ',"intended_trainer":"' + TP_Frontend_Backend_Bridge.projectName + '_trainer","entity_part_of_speech":"proper"}', properNounMongoDumpFromConceptDigger)

allProperNoun = re.findall('"entity_url"\s:\s"(.*?)"', properNounMongoDumpFromConceptDigger)

for properNoun_entity_url in allProperNoun:
    if ">" in properNoun_entity_url:
        #        if "(" in properNoun_text:
        #            properNoun_text = properNoun_text.replace("(", "")
        #        if ")" in properNoun_text:
        #            properNoun_text = properNoun_text.replace(")", "")
        synonym_collection.remove({"entity_url":properNoun_entity_url})
    else:
        print properNoun_entity_url

#commonNounAndAllAttributiveAndAllProperNoun = OnlyCommonNounAndAttributiveDump + properNounMongoDumpFromConceptDigger
insertVariableIntoMongoDb(properNounMongoDumpFromConceptDigger) #insert all attributive to mongo

mongoDumpFromConceptDigger = filter_CommonSense_mongoDumpFromConceptDigger(synonym_collection)
#this mongoDump must be written in a hardisk file, so that command line utility of mongodb can be used to automatically import this data into mongo database

t2 = time.time()
print "concept digger & file writing took " + str(t2-t1) + " seconds"
t1 = time.time()



"""
Append CommonSense training data in above mongoDump. For now we are hardwiring the commonsense training data
Later this data might also be sourced from Concept Digger component
"""
with open("data/mongoDumpOfCommonSenseTraining.txt", "r") as p:
    insertVariableIntoMongoDb(p.read())

p.close()



"""
Set intended_trainer of ~NoTag concepts to '[project]_
"""
f = open('data/mongoDB_Intended_Trainer_Setter_template.json', 'r')
p = open('data/mongoDB_Intended_Trainer_Setting.json', 'wb')
setter_template = f.read()
setter_template.replace("$Project", TP_Frontend_Backend_Bridge.projectName)
p.write(setter_template)
MongoCLI.mongo_query("noisy_NER", "entity", "data/mongoDB_Intended_Trainer_Setting.json")

t2 = time.time()
print "mongo flushing & importing took " + str(t2-t1) + " seconds"

"""
Start noisy NER process
"""
#TODO: soon we must call only NER, not the CP. Because CP takes more time for processing than NER
#try:
NERProcess = shell.initializeCommandNetProcessor_to_ComputeHighPriorityTrainingQuestions()

#except Exception as e:
#    print "CP couldn't be initialized!"
#    exit

"""
read catalogs in loop. extract plain text from them
"""
#TODO: change the lines below to accept both 'Training Portal' friendly JSON format, as well as plain-text format
#Presently it supports only plain-text format
"""
concatinate plain text from catalog with plain text of search text
"""
#TODO: we wont concatenate catalog with search text for now.
#because we are keeping both catalog & search inside /customer_files/foodweasel.com/ folder
#once we begin to store catalog files as JSON files 

"""
loop plain text input to NER
"""
# @profile
def NER_plain_text():
    from collections import defaultdict
    surface_txt_and_entity_tuple_MENTIONED_IN = defaultdict(list)

    catalogs = TP_Frontend_Backend_Bridge.getCatalogFiles()
    nerCache = {}
    """we cache the input & output of NER in nerCache. So if we are querying NER too much with repeated lines of text
    (say sending the word 'large' for tagging often, we can rather check NER's output from local cache than sending it to NER server).
    This cache is emptied everytime NER is run. We dont save it on hardisk purposely"""
    for catalog in catalogs:
        print catalog
        f = open(catalog, "r")
        fileName = os.path.basename(catalog)

        ner_input_line = f.readline()
        lineNumber = 1

        while ner_input_line != '':
            if nerCache.has_key(ner_input_line):
                nerDict = nerCache[ner_input_line]
            else:
                nerDict = eval(socket_sender.sendPacketOverSocket(config.NER_HostAddress, config.NER_Port, ner_input_line)) #eval is being used to convert string into dict object   
            #   print nerDict
                nerCache[ner_input_line] = nerDict
            """
            maintain dictionary of how each tag is stored in each sentence
            """
            for token in nerDict['tokens']:
                surface_text_and_entity_tuple_as_KEY = (token['id'], token['surface_text'])
                location_of_mention = "{0}.{1}".format(fileName, str(lineNumber))
                surface_txt_and_entity_tuple_MENTIONED_IN[surface_text_and_entity_tuple_as_KEY].append (location_of_mention)
            lineNumber = lineNumber + 1
            ner_input_line = f.readline()

        f.close()
    NERProcess.kill()
    """
    Calculate frequency of entity and update in mongodb
    """
    from pymongo import MongoClient
    client = MongoClient("127.0.0.1", 27017)
    db = client['noisy_NER']
    #     f = open('data/mongoDumpToSaveTaggedOutput.txt','wb')
    for surface_txt_and_entity_tuple in surface_txt_and_entity_tuple_MENTIONED_IN.keys():
        query = {"entity_url":"{0}".format(surface_txt_and_entity_tuple[0]),
                 "surface_text":"{0}".format(surface_txt_and_entity_tuple[1].encode('utf-8'))}
        update = {"$set":{"mentioned_in":surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple],
                          "frequency":len(surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple])
                          }}
    #         print query
    #         print update
        db.entity.update(query, update, upsert=True)
    #     f.write('{{"entity_url":"{0}" , "surface_text":"{1}" , "mentioned_in":{2} , "frequency":{3}}}\n'.format(surface_txt_and_entity_tuple[0],surface_txt_and_entity_tuple[1],str(surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple]).replace("'", ""),str(len(surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple]))))
    #     f.write('{"entity_url":"' + surface_txt_and_entity_tuple[0] + '" , "surface_text":"' + surface_txt_and_entity_tuple[1]  + 
    #             '" , "mentioned_in":' + str(surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple])  + 
    #             '" , "frequency":' +  str(len(surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple])) + '}\n')
    # f.close()
    # MongoCLI.mongo_import("noisy_NER", "entity", '"' + os.getcwd() + '/data/mongoDumpToSaveTaggedOutput.txt"','--upsertFields "entity_url,surface_text"')

NER_plain_text()
