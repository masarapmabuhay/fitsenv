# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages


from fitsapp.upload.models import Document
from fitsapp.upload.forms import DocumentForm
from fitsapp.upload.forms import DocumentSearchForm
from fitsapp.upload.forms import DocumentLocateForm

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.servers.basehttp import FileWrapper

import os, mimetypes, urllib

def upload_search(request):
    
    # Handle search
    if request.method == 'GET':
        form = DocumentSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            messages.info(request, 'Search query: ' + query)
        else:
            query = '';
    else:
        form = DocumentSearchForm() # A empty, unbound form
        
    # Load documents for the list page
    if query:
        documents = Document.objects.filter(docfile__contains=query)
    else:
        documents = Document.objects.all()

    paginator = Paginator(documents, 10) # Show 10 documents per page

    page = request.GET.get('page')
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        documents = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        documents = paginator.page(paginator.num_pages)

    # Render list page with the documents and the form
    return render_to_response(
        'upload/list.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )


def locate(request):
    
    # Handle search
    if request.method == 'GET':
        form = DocumentLocateForm(request.GET)
        if form.is_valid():
            # remove first 3 and last 3 characters of location, 
            # which is a randomized string
            location = form.cleaned_data['location'][3:-3]
        else:
            location = ''
            messages.error(request, 'Invalid utree/xml file.')
    else:
        form = DocumentLocateForm() # A empty, unbound form
        
    # Download document
    if location:
        document = Document.objects.get(id=location)
        if (document):
            # Prepare response file to be downloaded
            filename = 'static/media/' + document.docfile.name
            utree = FileWrapper(open(filename))
            mimetype = mimetypes.guess_type(os.path.basename(filename))[0]
            response = HttpResponse(utree, mimetype=mimetype)
            response['Content-Length']      = os.path.getsize(filename)
            response['Content-Disposition'] = "attachment; filename=%s"%filename

            # Update count            
            document.download_count += 1
            document.save()
            return response
        else:
		    messages.error(request, 'utree/xml file ' + location + ' not found.')            
    else:
		messages.error(request, 'utree/xml file is invalid.')
	
def upload(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid() and request.FILES['docfile'].name.lower().endswith(('.xml', '.utree')):

            newdoc = Document(docfile = request.FILES['docfile'], uploader = request.user, description = 'Test description.')
            newdoc.save()
            #if os.path.getsize(request.FILES['docfile']) > settings.MAX_UPLOAD_SIZE:
            #    messages.error(request, 'File size is too big.')
            #else:
            #    newdoc.save()

        else:
            messages.error(request, 'File type is not supported.')

        # Redirect to the document list after POST
        return HttpResponseRedirect(reverse('fitsapp.upload.views.upload'))

    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.filter(uploader=request.user)
    
    paginator = Paginator(documents, 10) # Show 10 documents per page

    page = request.GET.get('page')
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        documents = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        documents = paginator.page(paginator.num_pages)

    # Render list page with the documents and the form
    return render_to_response(
        'upload/list.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )
