'''
Created on 27-Jan-2015

@author: sb
'''
import time
import os
from subprocess import call, Popen

CP_path = os.path.expanduser('~/Smarter.Codes/src/Brain/2.UNDERSTAND/natural_language/CommandNet_Processor/src/main.py')

def initializeCommandNetProcessor_to_ComputeHighPriorityTrainingQuestions():
    p = Popen(['python', CP_path, 'ner', '5006', 'compute_high_priority_training_questions'])
    time.sleep(10)
    return p

def initializeCommandNetProcessor_to_TrainUIPWithLearntKnowledge():
    p = Popen(['python',CP_path, 'json', '5008', 'train_UIP_from_learnt_answers'])
    time.sleep(4)
    return p


def initializeCommandNetProcessor_to_enable_UIP_for_GenerateRecommendation():
    p = Popen(['python', CP_path, 'gml', '5012', 'train_UIP_from_learnt_answers'])
    time.sleep(4)
    return p
