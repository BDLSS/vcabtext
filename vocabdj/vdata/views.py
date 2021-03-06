from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from models import Document, Collection, Format

ACT_TAB = 'browse' # what tab on the UI should be shown active 

def index(request, pag_count=5):
    dlist = Document.objects.all().filter(status=5)
    try:
        pag_count = int(pag_count)
        if pag_count >= 100:
            pag_count = 100
    except (ValueError, TypeError): #A typeerror occurs if dlist is empty
        pag_count = 100
        
    paginator = Paginator(dlist, pag_count)
    page = request.GET.get('page')
    try:
        docs = paginator.page(page)
    except (PageNotAnInteger, TypeError):
        docs = paginator.page(1)
    except EmptyPage:
        docs = paginator.page(paginator.num_pages)
        
    context = {'docs': docs, 'active_tab': ACT_TAB}
    return render(request, 'index.html', context)

def detail(request, document_id):
    try:
        doc = Document.objects.get(pk=document_id)
        cats = doc.categories.all()
        tags = doc.tags.all()
        creators = doc.creators.all()
        contribs = doc.contributors.all()
    except Document.DoesNotExist:
        raise Http404
    context = {'document': doc, 'cats': cats, 'tags':tags,
                'creators': creators, 'contrib': contribs,
               'active_tab': ACT_TAB}
    return render(request, 'detail.html', context)

def native(request, document_id):
    '''Enables the downloading of a particular document.'''
    try:
        doc = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        raise Http404 
    return render(request, 'native.html', {'document': doc, 'active_tab': ACT_TAB})

def web(request, document_id):
    '''Enables the downloading of a particular document.'''
    try:
        doc = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        raise Http404 
    return render(request, 'web.html', {'document': doc, 'active_tab': ACT_TAB})

def download(request, document_id, ext_plus='', alt_mime=''):
    '''Enable direct downloads of the text.'''
    try:
        doc = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        raise Http404
    
    # What is the mime type?
    try:
        f = Format.objects.get(pk=doc.format)
        ext = f.download_extension
        mtype = f.native_mime_type
    except Format.DoesNotExist:
        ext = 'txt'
        mtype= 'text/plain'
    
    # Deal with content negotiation which might alter download
    if ext_plus:
        ext = '%s.%s'%(ext, ext_plus)
    if alt_mime:
        mtype = alt_mime
            
    # Dispatch the download.
    response = HttpResponse(mimetype=mtype)
    response['Content-Disposition']='attachment; filename=%s.%s'%(doc.name, ext)
    response.write(doc.text)
    return response

def collections(request):
    '''Enable links to documents grouped by collection.'''
    dcount = Document.objects.all().filter(status=5).count()
    clist = Collection.objects.all()
    ccount = clist.count()
    context = {'doc_count' : dcount, 'collection_list': clist,
               'col_count': ccount, 'active_tab': ACT_TAB}
    return render(request, 'collects.html', context)

def collection(request, collection_collection):
    '''Enable links to documents grouped by collection.'''
    c = collection_collection
    try:
        item = Collection.objects.get(pk=c)
    except Collection.DoesNotExist:
        raise Http404
    
    dlist = Document.objects.all().filter(status=5, collection=c)
    dcount = dlist.count()
    context = {'document_list' : dlist, 'collection': item,
               'doc_count' : dcount, 'active_tab': ACT_TAB}
    
    return render(request, 'collect_item.html', context)

def compact(request):
    dcount = Document.objects.all().filter(status=5).count()
    dlist = Document.objects.all().filter(status=5)
    clist = Collection.objects.all()
    ccount = clist.count()
    context = {'doc_count' : dcount, 'doc_list': dlist, 
               'collection_list': clist,
               'col_count': ccount, 'active_tab': ACT_TAB}
    return render(request, 'compact.html', context)
    
def download_latest(request, document_name):
    '''Download the latest version of document name.'''
    found_id = find_latest(document_name)
    if found_id:
        return download(request, found_id)
    else:
        raise Http404 

def download_version(request, doc_name, doc_version):
    '''Download a specific version of a document.'''
    found_id = find_version(doc_name, doc_version)
    if found_id:
        return download(request, found_id)
    else:
        raise Http404

def version_info(request, doc_name, doc_version):
    '''Goto the information page for a specific version of a document.'''
    found_id = find_version(doc_name, doc_version)
    if found_id:
        return detail(request, found_id)
    else:
        raise Http404

def current_info(request, document_name):
    '''Returns the information page of the current version.'''
    found_id = find_latest(document_name)
    if found_id:
        return detail(request, found_id)
    else:
        raise Http404
    
def find_latest(document_name):
    '''Returns the item id for the latest version of document name.'''
    try:
        dlist = Document.objects.all().filter(name=document_name)
    except Document.DoesNotExist:
        raise Http404
    latest = None
    latest_id = None
    for doc in dlist:
        check = doc.version_current
        if check > latest:
            latest = check
            latest_id = doc.id
    return latest_id

def find_version(doc_name, doc_version):
    '''Returns the item id for particular version of document name.'''
    try:
        found = Document.objects.get(name=doc_name, version_current=doc_version)
        answer = found.id
    except Document.DoesNotExist:
        answer = ''
    return answer

def find_id(doc_name, doc_version=''):
    '''Returns an item id based up document name and id.'''
    if doc_version:
        found_id = find_version(doc_name, doc_version)
        if not found_id:
            found_id = find_latest(doc_name)
    else:
        found_id = find_latest(doc_name)
    
    return found_id

def get_mime(docid, default='text/plain', ext='txt'):
    '''Returns the mime type and its extension for item with docid or returns default.'''
    try:
        doc = Document.objects.get(pk=docid)
    except Document.DoesNotExist:
        return default, ext
    
    try:
        f = Format.objects.get(pk=doc.format)
        return f.native_mime_type, f.download_extension 
    except Format.DoesNotExist:
        return default, ext
        
def content_neg(request, doc_name, doc_version=''):
    '''Enable content negotiation for doc with name.'''
    found_id = find_id(doc_name, doc_version)
    if not found_id:
        raise Http404
    default_type, unused = get_mime(found_id) # Type depends on item format

    try:
        accept = request.META['HTTP_ACCEPT']
        okay_types = accept.split(',')
    except KeyError:
        okay_types = ['text/html',] # tuple, needs comma
    #return HttpResponse('%s, %s'%(accept, okay_types))
    #okay_types = ['text/plagin','text/xmhl', 'text/htfml', 'appflication/rdf+xml'] # Test it
    
    downurl = '/data/%s/download'%found_id
    txt = 'text/plain'
    xml = 'text/xml'
    if default_type in okay_types: # This will work for any format
        return redirect(downurl)
        #return download(request, found_id)
    elif txt in okay_types: # Default, if request has no content type
        #return redirect(downurl)
        return download(request, found_id, 'txt', txt)
    elif xml in okay_types:
        #return redirect(downurl)
        return download(request, found_id, 'xml', xml)
    elif 'text/html' in okay_types:
        return redirect('/data/%s/'%found_id)
        return detail(request, found_id)
    else:
        return redirect(downurl)
        #return download(request, found_id)
    
    