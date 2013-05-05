from django.http import Http404, HttpResponse
from django.shortcuts import render

from models import Document, Collection, Format

def index(request):
    dlist = Document.objects.all().filter(status=5)
    context = {'document_list' : dlist}
    return render(request, 'index.html', context)

def detail(request, document_id):
    try:
        doc = Document.objects.get(pk=document_id)
        cats = doc.categories.all()
        tags = doc.tags.all()
    except Document.DoesNotExist:
        raise Http404 
    return render(request, 'detail.html', {'document': doc,
                        'cats': cats, 'tags':tags})

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
    '''Enable direct downloads of the text.'''
    try:
        doc = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        raise Http404
    
    # What is the mime type?
    try:
        f = Format.objects.get(pk=doc.format)
    except Format.DoesNotExist:
        f = 'text/plain'
    response = HttpResponse(mimetype=f.native_mime_type)
    
    # Dispatch the download.
    response['Content-Disposition'] = 'attachment; filename=%s'%doc.name
    response.write(doc.text)
    return response

def collections(request):
    '''Enable links to documents grouped by collection.'''
    dlist = Document.objects.all().filter(status=5)
    clist = Collection.objects.all()
    context = {'document_list' : dlist, 'collection_list': clist}
    return render(request, 'collects.html', context)
