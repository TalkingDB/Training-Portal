import CuisineSelection.cuisine_selection as cuisine
import CuisineSelection.generate_questions as questions
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, HttpResponse, render_to_response
from django.contrib.auth.decorators import login_required
from forms import CuisineForm
from django.contrib import messages
from django.http import Http404

import os
import json

root_dir_path = os.path.expanduser("~/Smarter.Codes/src")

@login_required
def select_cuisine(request):
    question_gen_progress = False

    if os.path.isfile(root_dir_path+'/progress.txt'):
        question_gen_progress = True

    current_cuisine = "Current Selected Cuisines are : "+ cuisine.get_current_cuisine()
    form = CuisineForm()
    if request.method == 'POST':
        form = CuisineForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data['cuisine']
            cuisine.select_cuisine(data)
            cuisine.set_current_cuisine(data)
            messages.add_message(request, messages.INFO, 'Cuisine '+ str(' '.join(data))+ " Selected!")
            return redirect('/cuisine_selection')

    return render_to_response(
        'review/cuisine.html',
        {'form': form, 'current_cuisines':current_cuisine, question_gen_progress:question_gen_progress}
        , context_instance=RequestContext(request)
    )


@login_required
@csrf_exempt
def generate_questions(request):

    if request.method == "GET":
        raise Http404

    # check if progress.txt exist in root_dir_path
    if os.path.isfile(root_dir_path+'question.txt'):
        # if yes return a dict with message
        return {'process': "Process already running."}
    else:
        # call retraining
        result = questions.generate_questions()
    return HttpResponse(json.dumps(result))



@login_required()
@csrf_exempt
def check_question_gen_progress(request):
    """
    Check if question generation is in progress by checking if file exist : question.txt

    As it is a xhr request send httpResponse of "string" true or "false"
    """
    if os.path.isfile(root_dir_path+'/question.txt'):
        return HttpResponse("true")

    return HttpResponse("false")