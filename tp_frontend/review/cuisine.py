import CuisineSelection.cuisine_selection as cuisine
from django.template import RequestContext
from django.shortcuts import render, redirect, HttpResponse, render_to_response
from django.contrib.auth.decorators import login_required
from forms import CuisineForm
from django.contrib import messages


@login_required
def select_cuisine(request):
    
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
        {'form': form, 'current_cuisines':current_cuisine}, context_instance=RequestContext(request)
    )
