import backend_config as config
from communicate_outside import MongoCLI
from communicate_outside import shell
from communicate_outside import socket_sender
import json
import networkx
import os
from pymongo.mongo_client import MongoClient
import sys
import time
sys.path.append(os.getcwd() + "/../")
import TP_Frontend_Backend_Bridge
import re

client = MongoClient("localhost", 27017)
db = client['noisy_NER']
synonym_collection = db['entity']
#created a new collection to store entity_meta_data
#entity_meta_data
#  enity_url
#  part_of_speech
#  node_id
entity_meta_data_collection = db['entity_meta_data']
#declared a global variable to be used for storing increasing node_id's 
global_node_id_increment = 0
#created a new collection to store command_meta_data
#command_meta_data
#  command_url
#  operation
#  node_id

Entity_to_Command_collection = db['Entity_to_Command']
command_meta_data_collection = db['command_meta_data']

#Pseudocode 
#1. find all common noun entities
#insert all common nount to database
#create new entity_meta_data collection then
#insert all common noun to that collection
#
#
#find all attributive
#
#loop through all attributive entity_urls
#   remove all from entity_collection
#   remove all from entity_meta_data
#
#create new entity_meta_data collection then
#insert all common noun to that collection 
#
#
#find all proper noun
#
#loop through all proper noun
#   remove all from entity_collection
#   remove all from entity_meta_data
#
#insert all proper noun into mongodb
#insert all poper noun into entity_meta_data 

def filter_CommonSense_mongoDumpFromConceptDigger(synonym_collection):
    # Open file containing data of commonsense linguist and add surface text to a list
    with open("data/mongoDumpOfCommonSenseTraining.txt", "r") as f:
        linguist_data = re.findall('"surface_text"\s:\s"(.*?)"', f.read())

    # remove lines having same surface text as commonsense linguist
    for data in linguist_data:
        synonym_collection.remove({"surface_text":data})

def dropTables():
    MongoCLI.mongo_collection_drop("noisy_NER", "entity")
    MongoCLI.mongo_collection_drop("noisy_NER", "Entity_to_Command")
    MongoCLI.mongo_collection_drop("noisy_NER", "entity_meta_data")

def insertVariableIntoMongoDb(variable, entity_part_of_speech):
    f = open("data/mongoDumpFromConceptDigger.txt", "wb")
    f.write(variable)
    """
    Forward entities, their surface_text to Noisy NER
    """
    import os
    MongoCLI.mongo_import("noisy_NER", "entity", os.getcwd() + "/data/mongoDumpFromConceptDigger.txt")
    f.close()
    if entity_part_of_speech:
        global_id_increment = 0
        unique_enities_with_noun = synonym_collection.aggregate([
                                                                {"$group":
                                                                {"_id": "$entity_url",
                                                                }
                                                                }])
        for entity in unique_enities_with_noun["result"]:
            entity_url = entity['_id']
            global_id_increment = global_id_increment + 1      
            enitity_part_of_speech_entity_url_unique_id_row = {"entity_url":entity_url, "entity_part_of_speech":entity_part_of_speech, "node_id":global_id_increment}
            entity_meta_data_collection.insert(enitity_part_of_speech_entity_url_unique_id_row)

"""
Read Seed Categories from TP Frontend
"""
#TODO: Change these lines
def set_categories_and_make_request_to_concept_digger():
    allCommonNounSeedCategories = '[["Category:Clothing",5,0,1]]'
    allAttributiveSeedCategories = '[["Category:Sizes_in_clothing",5,0,1],["Category:Color", 6,0,1]]'
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
    #find all common noun entities
    CommonNounMongoDumpFromConceptDigger = socket_sender.sendPacketOverSocket(config.conceptDiggerHostAddress, config.conceptDiggerPort, allCommonNounSeedCategories)

    CommonNounMongoDumpFromConceptDigger = re.sub('}', ',"intended_trainer":"' + TP_Frontend_Backend_Bridge.projectName + '_trainer"}', CommonNounMongoDumpFromConceptDigger)
    entity_part_of_speech = "common"
    insertVariableIntoMongoDb(CommonNounMongoDumpFromConceptDigger, entity_part_of_speech) #insert commonnounmongodump

    allAttributiveMongoDumpFromConceptDigger = socket_sender.sendPacketOverSocket(config.conceptDiggerHostAddress, config.conceptDiggerPort, allAttributiveSeedCategories)
    allAttributiveMongoDumpFromConceptDigger = re.sub('}', ',"intended_trainer":"' + TP_Frontend_Backend_Bridge.projectName + '_trainer"}', allAttributiveMongoDumpFromConceptDigger)
    allAttributive = re.findall('"entity_url"\s:\s"(.*?)"', allAttributiveMongoDumpFromConceptDigger)
    #print allAttributive
    for attributive_entity_url in allAttributive:
        if ">" in attributive_entity_url:
            #    if "(" in attributive_surface_text:
            #            attributive_surface_text = attributive_surface_text.replace("(","")
            #    if ")" in attributive_surface_text:
            #            attributive_surface_text = attributive_surface_text.replace(")","")
            synonym_collection.remove({"entity_url":attributive_entity_url})
            entity_meta_data_collection.remove({"entity_url":attributive_entity_url})
        else:
            print attributive_entity_url


    #CommonNounAndAttributiveDump = OnlyCommonNounDump + allAttributiveMongoDumpFromConceptDigger
    entity_part_of_speech = "attributive"
    insertVariableIntoMongoDb(allAttributiveMongoDumpFromConceptDigger, entity_part_of_speech) #insert all attributive to mongo


    properNounMongoDumpFromConceptDigger = socket_sender.sendPacketOverSocket(config.conceptDiggerHostAddress, config.conceptDiggerPort, allProperNounSeedCategories)
    properNounMongoDumpFromConceptDigger = re.sub('}', ',"intended_trainer":"' + TP_Frontend_Backend_Bridge.projectName + '_trainer"}', properNounMongoDumpFromConceptDigger)

    allProperNoun = re.findall('"entity_url"\s:\s"(.*?)"', properNounMongoDumpFromConceptDigger)

    for properNoun_entity_url in allProperNoun:
        if ">" in properNoun_entity_url:
            #        if "(" in properNoun_text:
            #            properNoun_text = properNoun_text.replace("(", "")
            #        if ")" in properNoun_text:
            #            properNoun_text = properNoun_text.replace(")", "")
            synonym_collection.remove({"entity_url":properNoun_entity_url})
            entity_meta_data_collection.remove({"entity_url":attributive_entity_url})
        else:
            print properNoun_entity_url

    #commonNounAndAllAttributiveAndAllProperNoun = OnlyCommonNounAndAttributiveDump + properNounMongoDumpFromConceptDigger
    entity_part_of_speech = "proper"
    insertVariableIntoMongoDb(properNounMongoDumpFromConceptDigger, entity_part_of_speech) #insert all attributive to mongo

    mongoDumpFromConceptDigger = filter_CommonSense_mongoDumpFromConceptDigger(synonym_collection)
    #this mongoDump must be written in a hardisk file, so that command line utility of mongodb can be used to automatically import this data into mongo database

    t2 = time.time()
    print "concept digger & file writing took " + str(t2-t1) + " seconds"
    t1 = time.time()

def insert_commonsense_training_data():
    """
    Append CommonSense training data in above mongoDump. For now we are hardwiring the commonsense training data
    Later this data might also be sourced from Concept Digger component
    """
    with open("data/mongoDumpOfCommonSenseTraining.txt", "r") as p:
        insertVariableIntoMongoDb(p.read(), 0)
    p.close()



def set_intented_trainer_of_no_tag_project():
    """
    Set intended_trainer of ~NoTag concepts to '[project]_
    """
    f = open('data/mongoDB_Intended_Trainer_Setter_template.json', 'r')
    p = open('data/mongoDB_Intended_Trainer_Setting.json', 'wb')
    setter_template = f.read()
    setter_template.replace("$Project", TP_Frontend_Backend_Bridge.projectName)
    p.write(setter_template)
    MongoCLI.mongo_query("noisy_NER", "entity", "data/mongoDB_Intended_Trainer_Setting.json")



def insertEntity_to_command_and_command_meta_data():
#   This function loads txt files from data folder then insert it directly into mongodb
#   folder. 
    MongoCLI.mongo_import("noisy_NER", "Entity_to_Command", os.getcwd() + "/data/Entity_to_Command.txt")
    MongoCLI.mongo_import("noisy_NER", "command_meta_data", os.getcwd() + "/data/command_meta_data.txt")
#   Get All Unique Entities from entity collection then insert into Entity_to_command
    unique_enities_with_noun = synonym_collection.aggregate([
                                                            {"$group":
                                                            {"_id": "$entity_url",
                                                            }
                                                            }])
#   Loop through all entities then insert unique entities with command = commandnet>Noun    
#   into Entity_to_command_collection 
#TODO: Later we will store PartofSpeech of entity inside this Entity_to_Command Collection
    for entity in unique_enities_with_noun["result"]:
        entity_url = entity['_id']
        global_id_increment = global_id_increment + 1      
        entity_to_command_row_from_entity_collection = {"command":"CommandNet>Noun", "entity_url":entity_url,}
        Entity_to_Command_collection.insert(enitity_part_of_speech_entity_url_unique_id_row)
"""
Start noisy NER process
"""
#TODO: soon we must call only NER, not the CP. Because CP takes more time for processing than NER
#try:
def start_command_net_processor():
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
    #     f.write('{{"entity_url":"{t>Un0}" , "surface_text":"{1}" , "mentioned_in":{2} , "frequency":{3}}}\n'.format(surface_txt_and_entity_tuple[0],surface_txt_and_entity_tuple[1],str(surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple]).replace("'", ""),str(len(surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple]))))
    #     f.write('{"entity_url":"' + surface_txt_and_entity_tuple[0] + '" , "surface_text":"' + surface_txt_and_entity_tuple[1]  + 
    #             '" , "mentioned_in":' + str(surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple])  + 
    #             '" , "frequency":' +  str(len(surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple])) + '}\n')
    # f.close()
    # MongoCLI.mongo_import("noisy_NER", "entity", '"' + os.getcwd() + '/data/mongoDumpToSaveTaggedOutput.txt"','--upsertFields "entity_url,surface_text"')
set_categories_and_make_request_to_concept_digger()
insert_commonsense_training_data() 
set_intented_trainer_of_no_tag_project()
insertEntity_to_command_and_command_meta_data()

t2 = time.time()
print "mongo flushing & importing took " + str(t2-t1) + " seconds"


#start_command_net_processor()
#NER_plain_text()