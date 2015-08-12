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

def remove_surface_text_from_mongoDB_which_were_claimed_by_CommonSenseTraining_mongoDumpFromConceptDigger(synonym_collection):
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
    MongoCLI.mongo_collection_drop("noisy_NER", "command_meta_data")
    
def mongoImport_via_String(string_with_json,collection):
    f = open("data/mongoDumpFromConceptDigger.txt", "wb")
    f.write(string_with_json)
    f.close()

    try:
        import os
        MongoCLI.mongo_import("noisy_NER", collection , os.getcwd() + "/data/mongoDumpFromConceptDigger.txt")
    except Exception as e:
        print e
        sys.exit()

"""
Read Seed Categories from TP Frontend
"""
#TODO: Change these lines
def set_categories_and_make_request_to_concept_digger():
    t1 = time.time()
    dropTables()
    debug_mode = True #saves time while debugging. skips making request to ConceptDigger, rather makes use of local cache
    
    allCommonNounSeedCategories = '[["Category:Clothing",5,0,1]]'
    allAttributiveSeedCategories = '[["Category:Sizes_in_clothing",5,0,1],["Category:Color", 6,0,1]]'
    allProperNounSeedCategories = '[["Category:Fashion_by_nationality", 4,0,1],["Category:Clothing_companies", 3,0,1]]'

#     Seed Dummy Categories for concept Digger 
#     allCommonNounSeedCategories = '[["Category:Food",1,1,0]]'
#     allAttributiveSeedCategories = '[["Category:Brand",1,1,0]'
#     allProperNounSeedCategories = '[["Category:Color", 1,1,0]]'

    """
    Forward seedCategories to 'Concept Digger (a.k.a Synonms Finder)' component
    """
    #find all common noun entities
    if debug_mode==True:
        opened_file = open('data/CommonNounMongoDumpFromConceptDigger.json','r')
        CommonNounMongoDumpFromConceptDigger = opened_file.read()
        opened_file.close()
    else:
        CommonNounMongoDumpFromConceptDigger = socket_sender.sendPacketOverSocket(config.conceptDiggerHostAddress, config.conceptDiggerPort, allCommonNounSeedCategories)

        opened_file = open('data/CommonNounMongoDumpFromConceptDigger.json','wb')
        opened_file.write(CommonNounMongoDumpFromConceptDigger)
        opened_file.close()
        
    CommonNounMongoDumpFromConceptDigger = re.sub('}(?:$|\n)', ',"intended_trainer":"' + TP_Frontend_Backend_Bridge.projectName + '_trainer"}\n', CommonNounMongoDumpFromConceptDigger)
    mongoImport_via_String(CommonNounMongoDumpFromConceptDigger,"entity") #insert commonnounmongodump
    allCommonNoun = re.findall('"entity_url"\s:\s"(.*?)"', CommonNounMongoDumpFromConceptDigger)
    uniqueCommonNoun = set(allCommonNoun)

    # Find Attributve entities
    if debug_mode==True:
        opened_file = open('data/allAttributiveMongoDumpFromConceptDigger.json','r')
        allAttributiveMongoDumpFromConceptDigger = opened_file.read()
        opened_file.close()
    else:
        allAttributiveMongoDumpFromConceptDigger = socket_sender.sendPacketOverSocket(config.conceptDiggerHostAddress, config.conceptDiggerPort, allAttributiveSeedCategories)

        opened_file = open('data/allAttributiveMongoDumpFromConceptDigger.json','wb')
        opened_file.write(allAttributiveMongoDumpFromConceptDigger)
        opened_file.close()
        
    allAttributiveMongoDumpFromConceptDigger = re.sub('}(?:$|\n)', ',"intended_trainer":"' + TP_Frontend_Backend_Bridge.projectName + '_trainer"}\n', allAttributiveMongoDumpFromConceptDigger)
    allAttributive = re.findall('"entity_url"\s:\s"(.*?)"', allAttributiveMongoDumpFromConceptDigger)
    uniqueAttributive = set(allAttributive)
    mongoImport_via_String(allAttributiveMongoDumpFromConceptDigger,"entity") #insert all attributive to mongo

    # Find Proper Noun entities
    if debug_mode==True:
        opened_file = open('data/properNounMongoDumpFromConceptDigger.json','r')
        properNounMongoDumpFromConceptDigger = opened_file.read()
        opened_file.close()
    else:
        properNounMongoDumpFromConceptDigger = socket_sender.sendPacketOverSocket(config.conceptDiggerHostAddress, config.conceptDiggerPort, allProperNounSeedCategories)

        opened_file = open('data/properNounMongoDumpFromConceptDigger.json','wb')
        opened_file.write(properNounMongoDumpFromConceptDigger)
        opened_file.close()

    properNounMongoDumpFromConceptDigger = re.sub('}(?:$|\n)', ',"intended_trainer":"' + TP_Frontend_Backend_Bridge.projectName + '_trainer"}\n', properNounMongoDumpFromConceptDigger)
    
    allProperNoun = re.findall('"entity_url"\s:\s"(.*?)"', properNounMongoDumpFromConceptDigger)
    uniqueProperNoun = set(allProperNoun)
    mongoImport_via_String(properNounMongoDumpFromConceptDigger,"entity") #insert all ProperNoun to mongo

    remove_surface_text_from_mongoDB_which_were_claimed_by_CommonSenseTraining_mongoDumpFromConceptDigger(synonym_collection)

    #write common noun, attributive, proper noun in entity_meta_data.
    # But common noun, with attributive, then overwrite it with proper noun
    dict_entity_meta_data= {}
    for entity_url in uniqueCommonNoun:
        dict_entity_meta_data[entity_url] = 'common'
        
    for entity_url in uniqueAttributive:
        dict_entity_meta_data[entity_url] = 'attributive'
    
    for entity_url in uniqueProperNoun:
        dict_entity_meta_data[entity_url] = 'proper'
        
    mongodb_json_buffer = ''
    for entity_url in dict_entity_meta_data:
        if entity_url.find('>') > 0:
            mongodb_json_buffer = mongodb_json_buffer + '{"entity_url":"' + entity_url + '", "entity_part_of_speech":"' + dict_entity_meta_data[entity_url] + '"}\n'
    mongoImport_via_String(mongodb_json_buffer,"entity_meta_data")
    
    t2 = time.time()
    print "concept digger & file writing took " + str(t2-t1) + " seconds"
    t1 = time.time()

def insert_commonsense_training_data():
    """
    Append CommonSense training data in above mongoDump. For now we are hardwiring the commonsense training data
    Later this data might also be sourced from Concept Digger component
    """
    with open("data/mongoDumpOfCommonSenseTraining.txt", "r") as p:
        mongoImport_via_String(p.read(),"entity")
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
    MongoCLI.mongo_import("noisy_NER", "Entity_to_Command", os.getcwd() + "/data/Entity_to_Command.json")
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
        entity_to_command_row_from_entity_collection = {"command":"CommandNet>Noun", "entity_url":entity_url}
        Entity_to_Command_collection.insert(entity_to_command_row_from_entity_collection)
"""
Start noisy NER process
"""
#TODO: soon we must call only NER, not the CP. Because CP takes more time for processing than NER
#try:
def start_command_net_processor():
    return shell.initializeCommandNetProcessor_to_ComputeHighPriorityTrainingQuestions()

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
def NER_plain_text(NERProcess):
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
insertEntity_to_command_and_command_meta_data()
insert_commonsense_training_data() 
set_intented_trainer_of_no_tag_project()




NERProcess = start_command_net_processor()
NER_plain_text(NERProcess)
