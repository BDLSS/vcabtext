from django.http import Http404, HttpResponse
from django.shortcuts import render

from models import Document

def index(request):
    dlist = Document.objects.all()
    context = {'document_list' : dlist}
    return render(request, 'index.html', context)

def detail(request, document_id):
    try:
        doc = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        raise Http404 
    return render(request, 'detail.html', {'document': doc})

def native(request, document_id):
    '''Enables the downloading of a particular document.'''
    try:
        doc = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        raise Http404 
    return render(request, 'native.html', {'document': doc})

def web(request, document_id):
    '''Enables the downloading of a particular document.'''
    try:
        doc = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        raise Http404 
    return render(request, 'web.html', {'document': doc})

def download(request, document_id):
    try:
        doc = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        raise Http404
    response = HttpResponse(mimetype='application/rdf+xml')
    response['Content-Disposition'] = 'attachment; filename=%s'%doc.name
    response.write(doc.text)
    return response