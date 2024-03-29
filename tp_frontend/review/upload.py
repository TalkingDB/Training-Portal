from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from accuracy import initialization

from models import Document
from forms import DocumentForm

def upload(request):
    """

    """
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            inputFile = request.FILES['docfile']
            query_type = "mass_input"
            one_res_format = form.cleaned_data['only_1st_restaurant'] or False
            for_matching_algo = form.cleaned_data['for_matching_algo'] or False
            outputFile = initialization(inputFile, query_type, one_res_format, for_matching_algo)
            newdoc = Document(docfile = request.FILES['docfile'], outfile = outputFile)
            newdoc.save()

            # Redirect to the document list after POST
            return redirect('/bulk-testing')
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'review/upload.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )
