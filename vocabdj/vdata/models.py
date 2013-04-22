from django.db import models
from django.contrib.auth.models import User


# Models the main Document model depends upon
# =======================================================================
class Format(models.Model):
    '''The system needs to store different types of format.'''
    h = 'The very brief way of referring to this format.'
    format = models.CharField(max_length=20, primary_key=True, help_text=h)
    
    h = 'If the format is an acronym, what does it stand for?'
    expanded_acronym = models.CharField(max_length=250, default='', help_text=h)
    
    h = 'Can this format be converted into HTML.'
    html_convert_enable = models.BooleanField(default=True, verbose_name='HTML enabled', help_text=h)
    
    h = 'What method should be used convert the format into HTML.'
    html_convert_method = models.CharField(max_length=20, default='', blank=True, help_text=h)
    
    h = 'A convert method might deal with multiple formats if command line options differ.' 
    html_convert_options = models.CharField(max_length=250, default='', blank=True,  help_text=h)
    
    h = 'Can this format be download in its native form?'
    native_enabled = models.BooleanField(default=True, verbose_name='Native enabled', help_text=h)
    
    h = 'Mime type to send to browser when sending none html files. (eg. application/rdf+xml)'
    native_mime_type = models.CharField(max_length=200, default='',  blank=True, help_text=h)
        
    notes = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.format
    
class Collection(models.Model):
    '''A document can be part of a broad collection.'''
    h = 'A short name for this collection. eg. usedox'
    collection = models.CharField(max_length=20, primary_key=True, help_text=h)
    
    h = 'A longer (friendly) name to refer to this collection. eg. Used by Oxford'
    longer_name = models.CharField(max_length=50, default='', help_text=h)
    
    h = 'Description to use at the top of any pages used to show items in collections.'
    description = models.TextField(blank=True, help_text=h)
    
    h = 'A link to more information about this collection if description is not enough.'
    url_about_collection = models.URLField(blank=True, help_text=h)
    
    notes = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.collection
    
class Tag(models.Model):
    '''A document can have user defined tags.'''
    h = 'A tag should ideally be a single word, (eg. keyword HTML meta tag)'
    tag = models.CharField(max_length=30, primary_key=True, help_text=h)
    
    h = 'You can keep brief notes about this tag for internal use.'
    notes = models.CharField(max_length=250, blank=True, help_text=h)
    
    def __unicode__(self):
        return self.tag
    
class Category(models.Model):
    '''A document can have user defined tags.'''
    h = 'A category can be up to 50 chars long and can contain spaces.'
    category = models.CharField(max_length=50, primary_key=True, help_text=h)
    
    h = 'You can keep brief notes about this category for internal use.'
    notes = models.CharField(max_length=250, blank=True, help_text=h)
    
    def __unicode__(self):
        return self.category
    
    class Meta():
        verbose_name_plural = 'Categories'


# The main model used to hold documents and their meta information.
# =======================================================================
class Document(models.Model):
    '''A representation of vocab document.'''
    h = 'A short name commonly used to refer to this document. e.g. "Dublin Core"'
    name = models.CharField(max_length=50, help_text=h)
    
    
    statuses = (('1', 'New'), ('3', 'Review'),
                ('5', 'Public'), ('7', 'Hidden'),
                ('9', 'Delete'))
    h = 'If "Public" this document is also visible outside the admin interface.'
    status = models.CharField(max_length=5, default='1', help_text=h, choices=statuses)
    
    sources = (('1', 'Internal'), ('2', 'External'), ('3', 'Mixture'))
    h = 'Where did this file originate?'
    source = models.CharField(max_length=5, blank=True, help_text=h, choices=sources)
    
    
    h = 'What format is this document.'
    format = models.ForeignKey(Format, null=True, blank=True, help_text=h)
    
    h = 'Documents get grouped into broad collections.'
    collection = models.ForeignKey(Collection, null=True, blank=True, help_text=h)
    
    h = 'You can assign categories to this document. Ask the site admin to add new choices.'
    categories = models.ManyToManyField(Category, null=True, blank=True, help_text=h, related_name='categories')
    
    h = 'You can assign tags to this document and create new ones if required.'
    tags = models.ManyToManyField(Tag, null=True, blank=True, help_text=h, related_name='tags')
    
    h = "The namespace commonly used or one you'd like users to use. e.g. 'dc' as in xmlns:dc="
    suggested_namespace = models.CharField(max_length=20, blank=True, help_text=h)
    
    h = 'A short summary of this document. (50 chars, no HTML tags)'
    brief_description = models.CharField(max_length=50, blank=True, help_text=h)
    
    h = 'An additional summary of this document, if required. '
    description = models.TextField(blank=True, help_text=h)
  
    h = 'You can keep any notes about this document for internal use.'
    notes = models.TextField(blank=True, help_text=h)

    h = 'This is used as namespace identifier and can be used to fetch original text.'
    namespace_uri = models.URLField(blank=True, help_text=h)
    
    h = 'If exists, the URL documentation for this original document.'
    home_doc_url = models.URLField(blank=True, help_text=h)
    
    h = 'Contact for this document within the system? Who might have modify rights.'
    maintainer = models.ForeignKey(User, null=True, blank=True, help_text=h, related_name='maintainer')
    
    h = 'A comma separated list of people or organisations who created the document.'
    creators = models.CharField(max_length=250, blank=True, help_text=h)
    
    h = 'A comma separated list of people or organisations who contributed to the document.'
    contributors = models.CharField(max_length=250, blank=True, help_text=h)
    
        
    # ---------------------------------------------------------------
    # Fields that hold the native documents, the 1st is V.IMPORTANT
    # ---------------------------------------------------------------   
    h = 'The raw document e.g. RDF, XSD. (Cut and paste from text file editor, or use auto text options.)'
    text = models.TextField(blank=True, help_text=h)

    h = 'Should the HTML information be shown?'
    html_enabled = models.BooleanField(default=True, help_text=h)
    
    h = 'HTML information not automatically maintained.'
    html_doc = models.TextField(blank=True, help_text=h)
    
    h = 'Should HTML information be automatically maintained from the Text?'
    html_auto_enabled = models.BooleanField(default=True, help_text=h)
    
    h = 'The automatic HTML documentation/representation of this document.'
    html_auto_doc = models.TextField(blank=True, help_text=h)
    
    # ---------------------------------------------------------------
    # Fields that automate text loading.
    # ---------------------------------------------------------------
    # The following options effect how the field text gets populated.
    h = 'Reset text from an uploaded a file.'
    text_upload = models.FileField(upload_to='rawtext/%Y/%m/%d', blank=True, help_text=h)
    
    h = 'Reset text by downloading from namespace uri . (CHECK IT IS SAFE)'
    text_fetch_enabled = models.BooleanField(default=False, help_text=h)
    
    h = 'Reset text from an uploaded compressed file. (accepts zip, gz, bz2)'
    compress_upload = models.FileField(upload_to='compress/%Y/%m/%d', blank=True, help_text=h)
    
    h = 'If resetting by compressed file, the main file with the "includes".'
    compress_start_doc = models.CharField(max_length=30, blank=True, help_text=h)
    
    h = 'In addition to the main file, automatically add the included files as documents.'
    compress_includes_auto_add = models.BooleanField(default=True, help_text=h)
    
    # ---------------------------------------------------------------
    # Fields that link between different version.
    # ---------------------------------------------------------------
    h = 'If more than one version of this document exists, what version is this?'
    v = 'Current version'
    version_current = models.CharField(max_length=20, blank=True, help_text=h, verbose_name=v)
    
    h = 'If exists, you can make a link to a PREVIOUS version of this document.'
    v = 'Previous version'
    version_previous = models.ForeignKey('self', null=True, blank=True,
                                         help_text=h, related_name='previous',
                                         verbose_name=v)
    
    h = 'If exists, you can make a link to a NEXT version of this document.'
    v = 'Next version'
    version_next = models.ForeignKey('self', null=True, blank=True, help_text=h,
                                     related_name='next', verbose_name=v)
    
    h = 'Does this document EXTEND an existing document?'
    v = 'Extends document'
    version_extends = models.ForeignKey('self', null=True, blank=True, help_text=h,
                                        related_name='extends', verbose_name=v)
    
    h = 'If this document was automatically added, what document triggered the loading.'
    v = "Document's parent"
    version_parent = models.ForeignKey('self', null=True, blank=True, help_text=h,
                                       related_name='parent', verbose_name=v)
  
    h = 'Is there another document RELATED to this one? '
    v = 'Related document'
    version_related = models.ForeignKey('self', null=True, blank=True, help_text=h,
                                        related_name='also', verbose_name=v)
    
    # ---------------------------------------------------------------
    # Fields containing dates
    # ---------------------------------------------------------------
    date_added = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    date_modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    h = 'A rough date (to year accuracy) when this document was first made public.'
    v = "Document's date"
    date_document = models.DateTimeField(blank=True, null=True, help_text=h, verbose_name=v)
    
    def __unicode__(self):
        return '%s - %s'%(self.id, self.name)
    
    class Meta:
        ordering = ['name']
    