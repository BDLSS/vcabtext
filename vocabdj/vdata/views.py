from django.http import Http404
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
