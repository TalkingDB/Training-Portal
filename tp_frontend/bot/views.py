from django.shortcuts import render, redirect
from django.http import HttpResponse
from bot.models import ProgressStats

from subprocess import Popen
import json

def bot(request, process = None):
    if request.is_ajax():
        context = __check_step()
        if (process == 'one'):
            
            if "process_started" not in context['data']:
                data = __subprocess()
                
        return HttpResponse(json.dumps(context), content_type="application/json")
    else:
        return render(request, 'bot/index.html', {})
    
def __check_step():
    context = {}
    stats = ProgressStats.objects.filter(done=None)
    if stats:
        count = 0
        for i in stats:
            if i.done is not None:
                count += 1
            else:
                context = {
                       "data" : {
                               "process_started" : True,
                               "started" : str(i.started),
                               "done" : i.done,
                               "step" : i.step,
                               "percentage_done" : i.percentage_done,
                               "remaining_time" : i.remaining_time,
                               }
                       }
            
    else:
        context = {
                   "data" : {
                             "step" : 1,
                             }
                   }
    return context

def __subprocess():
    p = Popen(['python', '/home/sb/NetBeansProjects/AI_training_portal/main.py'])
    return p
