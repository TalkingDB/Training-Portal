import backend_config as config
from communicate_outside import socket_sender
from communicate_outside import shell
import os
import sys;sys.path.append(os.getcwd() + "/../")
import TP_Frontend_Backend_Bridge
from pymongo.mongo_client import MongoClient

client = MongoClient("localhost",27017)
db = client['noisy_NER']
entity_collection = db['questions']
synonym_collection = db['entity']


def NER_plain_text(flush):
    """
    Start ner process for processing catalogs.
    """
    flush_previous_data(flush)
    NERProcess = shell.initializeCommandNetProcessor_to_ComputeHighPriorityTrainingQuestions()
    from collections import defaultdict

    surface_txt_and_entity_tuple_MENTIONED_IN = defaultdict(list)
    
    catalogs =  TP_Frontend_Backend_Bridge.getCatalogFiles()
    nerCache = {}
    """we cache the input & output of NER in nerCache. So if we are querying NER too much with repeated lines of text
    (say sending the word 'large' for tagging often, we can rather check NER's output from local cache than sending it to NER server).
    This cache is emptied everytime NER is run. We dont save it on hardisk purposely"""
    for catalog in catalogs:
        print catalog
        f = open(catalog,"r")
        fileName = os.path.basename(catalog)
        
        ner_input_line = f.readline()
        lineNumber = 1
        
        while ner_input_line != '':
            if nerCache.has_key(ner_input_line):
                nerDict = nerCache[ner_input_line]
            else:
                nerDict = eval(socket_sender.sendPacketOverSocket(config.NER_HostAddress, config.NER_Port, ner_input_line)) #eval is being used to convert string into dict object   
#                 print nerDict
                nerCache[ner_input_line] = nerDict
            """
            maintain dictionary of how each tag is stored in each sentence
            """
            for token in nerDict['tokens']:
                surface_text_and_entity_tuple_as_KEY = (token['id'],token['surface_text'])
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
    client = MongoClient("127.0.0.1",27017)
    db = client['noisy_NER']
#     f = open('data/mongoDumpToSaveTaggedOutput.txt','wb')
    for surface_txt_and_entity_tuple in surface_txt_and_entity_tuple_MENTIONED_IN.keys():
        query = {"entity_url":"{0}".format(surface_txt_and_entity_tuple[0]) ,
                          "surface_text":"{0}".format(surface_txt_and_entity_tuple[1].encode('utf-8'))}
        update = {"$set":{"mentioned_in":surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple],
                          "frequency":len(surface_txt_and_entity_tuple_MENTIONED_IN[surface_txt_and_entity_tuple])
                          }}
        db.entity.update(query,update,upsert=True)
    if not flush:
        update_question_collection()

def flush_previous_data(flush):
    if flush:
        synonym_collection.update({},{
            "$unset":{
                "mentioned_in":1, "disapproved_by_trainer":1,
                "approved_by_trainer":1, "frequency":1,
                "skipped_by_trainer":1 }
            },
        upsert = False, multi = True)
        entity_collection.remove({})
    else:
        synonym_collection.update({},{
            "$unset":{
                "mentioned_in":1, "frequency":1
                }
            },
        upsert = False, multi = True)
    return

def update_question_collection():
    """

    :return:
    """
    entity_collection.update({},{
            "$unset":{"frequency":1}
            },
        upsert = False, multi = True)

    questions = entity_collection.find({})

    for question in questions:
        if ">" in question['question']:
            concept = "entity_url"
        else:
            concept = "surface_text"
        frequency = get_frequency(concept, question['question'])
        entity_collection.update({"question":question['question']},{
            "$set":{"frequency":frequency}
            },
        upsert = False)

def get_frequency(conceptType, entity):
    """

    :return:
    """
    data = synonym_collection.aggregate([
        { "$match":{"intended_trainer":TP_Frontend_Backend_Bridge.projectName + "_trainer",
                    conceptType:entity
                    }
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
        }
    ])
    return data['result'][0]['freq']