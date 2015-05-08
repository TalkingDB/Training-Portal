import backend_config as config
from communicate_outside import socket_sender
from communicate_outside import shell

import os
import sys;sys.path.append(os.getcwd() + "/../")
import TP_Frontend_Backend_Bridge



def NER_plain_text():
    """
    Start ner process for processing catalogs.
    """
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
            print ner_input_line
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