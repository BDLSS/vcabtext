from django.db import models

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
    
class Document(models.Model):
    '''A representation of vocab document.'''
    h = 'A short name commonly used to refer to this document. eg. "Dublin Core"'
    name = models.CharField(max_length=50, help_text=h)
    
    h = 'What format is this document.'
    format = models.ForeignKey(Format, null=True, blank=True, help_text=h)
    
    h = 'Documents get grouped into broad collections.'
    collection = models.ForeignKey(Collection, null=True, blank=True, help_text=h)
    
    h = 'If exists, the commonly used namespace for this document. eg "dc" as in xmlns:dc='
    namespace = models.CharField(max_length=20, blank=True, help_text=h)
    
    h = 'A short summary of this document. (50 chars, no HTML tags)'
    brief_description = models.CharField(max_length=50, blank=True, help_text=h)
    
    h = 'An additional summary of this document, if required. '
    description = models.TextField(blank=True, help_text=h)
  
    h = 'You can keep any notes about this document for internal use.'
    notes = models.TextField(blank=True, help_text=h)

    h = 'If exists, the original url this documents comes from. (Auto fetch uses this).'
    home_url = models.URLField(blank=True, help_text=h)
    
    h = 'If exists, the URL documentation for this original document'
    home_doc_url = models.URLField(blank=True, help_text=h)
    
    
    # ---------------------------------------------------------------
    # Fields that hold the native documents, the 1st is V.IMPORTANT
    # ---------------------------------------------------------------    
    h = 'The raw document. (Cut and paste from text file editor, or use auto text options.)'
    text = models.TextField(blank=True, help_text=h)

    h = '*Should the text version be automatically processed and shown as HTML?'
    html_enabled = models.BooleanField(default=False, help_text=h)
    
    h = 'The HTML documentation/representation of this document. (Manual edit is possible).'
    html_doc = models.TextField(blank=True, help_text=h)
    
    # ---------------------------------------------------------------
    # Fields that automate text loading.
    # ---------------------------------------------------------------
    # The following options effect how the field text gets populated.
    h = '*Reset text from an uploaded a file.'
    #text_upload = models.FileField(upload_to=None, blank=True, help_text=h)
    
    h = '*Reset text by downloading from a home url. (CHECK IT IS SAFE)'
    text_fetch_enabled = models.BooleanField(default=False, help_text=h)
    
    h = '*Reset text from an uploaded compressed file. (accepts zip, gz, bz2)'
    #compress_upload = models.FileField(upload_to=None, blank=True, help_text=h)
    
    h = 'If resetting by compressed file, the main file with the "includes".'
    compress_start_doc = models.CharField(max_length=30, blank=True, help_text=h)
    
    h = '*In addition to the main file, automatically add the included files as documents.'
    compress_includes_auto_add = models.BooleanField(default=False, help_text=h)
    
    # ---------------------------------------------------------------
    # Fields that link between different version.
    # ---------------------------------------------------------------
    h = 'If more than one version of this document exists, what version is this?'
    version_current = models.CharField(max_length=20, blank=True, help_text=h)
    
    h = 'If exists, you can make a link to a PREVIOUS version of this document.'
    version_previous = models.ForeignKey('self', null=True, blank=True, help_text=h, related_name='previous')
    
    h = 'If exists, you can make a link to a NEXT version of this document.'
    version_next = models.ForeignKey('self', null=True, blank=True, help_text=h, related_name='next')
    
    h = 'Does this document extend an existing document?'
    version_extends = models.ForeignKey('self', null=True, blank=True, help_text=h, related_name='extends')
    
    h = 'If this document was automatically added, what document triggered the loading.'
    version_parent = models.ForeignKey('self', null=True, blank=True, help_text=h, related_name='parent')
  
    def __unicode__(self):
        return '%s - %s'%(self.id, self.name)
    
    