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
    