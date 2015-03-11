'''
Created on 27-Jan-2015

@author: sb
'''
import time
import os
from subprocess import call, Popen

def initializeCommandNetProcessor_to_ComputeHighPriorityTrainingQuestions():
    #TODO : make the following path RELATIVE

    p = Popen(['python', os.getcwd() + '/../../CommandNet_Processor/src/main.py', 'ner', '5006', 'compute_high_priority_training_questions'])
    time.sleep(10)
    return p

def initializeCommandNetProcessor_to_TrainUIPWithLearntKnowledge():
    #TODO : make the following path RELATIVE

    p = Popen(['python', os.getcwd() + '/../../CommandNet_Processor/src/main.py', 'gml', '5008', 'train_UIP_from_learnt_answers'])
    time.sleep(10)
    return p

