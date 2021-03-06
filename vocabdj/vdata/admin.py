from django.contrib import admin, messages
from vdata.models import Format, Collection, Document, Tag, Category, Agent
from urllib2 import URLError
from datetime import datetime
import urllib2
               
ENABLE_FIELDSETS = True

from htmlauto import DoHtml

class FormatAdmin(admin.ModelAdmin):
    list_display = ('format', 'expanded_acronym', 'html_convert_enable', 'native_mime_type')
    list_filter = ('date_modified',)
    readonly_fields = ('date_added', 'date_modified')

admin.site.register(Format, FormatAdmin)

class CollectionAdmin(admin.ModelAdmin):
    list_display = ('collection', 'longer_name')
    list_filter = ('date_modified',)    
    readonly_fields = ('date_added', 'date_modified')

admin.site.register(Collection, CollectionAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'notes')
    list_filter = ('date_modified',)    
    readonly_fields = ('date_added', 'date_modified')

admin.site.register(Tag, TagAdmin)

class CatAdmin(admin.ModelAdmin):
    list_display = ('category', 'notes')
    list_filter = ('date_modified',)    
    readonly_fields = ('date_added', 'date_modified')

admin.site.register(Category, CatAdmin)

class AgentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'atype')
    list_filter = ('date_modified', 'atype')
    readonly_fields = ('date_added', 'date_modified')
    
admin.site.register(Agent, AgentAdmin)

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'version_current', 'status', 'format', 'collection', 'maintainer')
    list_display_links = ('id', 'name')
    list_filter = ('date_modified', 'status', 'collection', 'maintainer', )
    date_hierarchy = 'date_document'
    readonly_fields = ('date_added', 'date_modified', 'date_last_auto',
                       'auto_log', 'maintainer')
    filter_horizontal = ('categories', 'tags', 'creators', 'contributors')
    
    raw_id_fields = ('version_extends','version_parent', 'version_related', 'version_previous', 'version_next')
    
    actions = None # Disable the bulk delete option
    
    if ENABLE_FIELDSETS:
        hide = ('collapse', 'wide', 'extrapretty')
        fieldsets = (
                        (None, {'fields': ('name', )}),
                        
                        ('Minimum information needed', {
                              'classes': hide,
                              'description': 'These fields are REQUIRED before this item can be public.',
                              'fields':
                              ('status', 'brief_description', 'format', 'collection',
                                    'text')
                              }),
                      
                        ('Creators and Contributors ', {
                            'classes': hide,
                            'description': 'You can assign creators and contributors if you wish.',
                            'fields': ('creators',
                                       'contributors',
                                       ),
                              }),
                     
                        ('Categories and Tags', {
                            'classes': hide,
                            'description': 'You can assign categories and tags if you wish.',
                            'fields': ('categories',
                                       'tags',
                                       ),
                              }),
                     
                        ('Auto text options', {
                            'classes': hide,
                            'description': """WARNING WARNING If enabled these
                            fields automatically update the text field. Text
                            upload has priority over get url if both are ticked.
                             WARNING WARNING.""",
                            'fields': ('text_fetch_enabled',
                                       'text_upload',
                                       'auto_get_enabled',
                                       'auto_get_url',
                                       )
                              }),
                     
                        ('HTML contents', {
                            'classes': hide,
                            'description': 'A document has a landing page, the HTML to use.',
                            'fields': (
                                       'html_enabled',
                                       'html_doc',
                                       'html_auto_enabled',
                                       'html_auto_doc'
                                       ),
                              }),
                     
                        ('More details', {
                            'classes': hide,
                            'description': 'If general fields are used less often they can be moved here.',
                            'fields': ('source',
                                       'suggested_namespace',
                                       'description',
                                       'notes',
                                       ),
                              }),
                     
                        ('URL and URI', {
                            'classes': hide,
                            'description': 'A place to put some url and some uri',
                            'fields': ('namespace_uri',
                                       'home_doc_url',
                                       'persistent_url1',
                                       'persistent_url2',
                                       ),
                              }),
                     
                        ('Advanced auto text options', {
                            'classes': hide,
                            'description': """These advanced feature do not
                            currently do anything. They are here to enable
                            future development. """,
                            'fields': ('compress_start_doc',
                                       'compress_includes_auto_add',
                                       'compress_upload',
                                       'auto_make_text',
                                       'auto_make_source',
                                       )
                              }),
                                          
                        ('Version information', {
                            'classes': hide,
                            'description': 'These fields let you make links between versions.',
                            'fields': ('version_current',
                                       'date_document',
                                       'version_previous',
                                       'version_next'),
                              }),
                        ('Other version info', {
                            'classes': hide,
                            'description': 'These fields let you make links with other documents.',
                            'fields': ('version_extends',
                                       'version_parent',
                                       'version_related',),
                              }),
                     
                        ('Read only', {
                            'classes': hide,
                            'description': 'These fields are for use by library staff mainly.',
                            'fields': ('maintainer',
                                       'date_added',
                                       'date_modified',
                                       'date_last_auto',
                                       'auto_log',
                                       ),
                              }),
                     
                      )
        

    def queryset(self, request):
        '''Control what items get shown on the list display.'''
        qs = super(DocumentAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(maintainer=request.user)
        
    # ---------------------------------------------------------------
    # Custom save handler and best method of fetching text.
    # ---------------------------------------------------------------
    def save_model(self, request, doc, form, change):
        '''Add custom save options to admin.'''
        if doc.maintainer == None:
            doc.maintainer = request.user

        doc.name = str(doc.name).lower().replace(' ', '') #lower+remove spaces
        doc.save() # Save the model first to deal with any errors.
        
        # Enable the setting of the text field via file upload.
        if doc.text_fetch_enabled: # This has more priority
            self.text_fetch(request, doc)
        else:
            # Enable the setting of the text field via a url.
            if doc.auto_get_enabled: # This has less priority
                self.auto_get_text(request, doc)
                
        # Enable the setting of the html field via text.
        if doc.html_auto_enabled:
            self.html_auto(request, doc)
        
        self.update_status(request, doc)
        
    def update_status(self, request, doc):  
        '''Update status if data is missing.'''
        # Report any missing items
        okay = True
        if doc.brief_description == '':
            messages.info(request, 'BRIEF DESCRIPTION will be needed.')
            okay = False
        if doc.format == None:
            messages.info(request, 'FORMAT will be needed.')
            okay = False
        if doc.collection == None:
            messages.info(request, 'COLLECTION will be needed.')
            okay = False
        if doc.text == '':
            messages.info(request, 'TEXT is current empty.')
            okay = False
    
        # Feedback and edit status if needed.
        if not okay:                   
            doc.status = 3
            self.log_auto(request, doc, 'public2review%s')
            doc.save()
            m = 'Review status enabled, see messages above for information needed.'
            messages.warning(request, m)          
      
    def text_fetch(self, request, doc):
        '''Load the text field from the uploaded filed.'''
        messages.warning(request, 'Trying to set text from uploaded file.')
        uploaded = doc.text_upload # this contains the file information
        if uploaded:
            doc.text = uploaded.read()
            messages.success(request, 'Text successfully loaded.')
            doc.text_fetch_enabled = False
            self.log_auto(request, doc, 'file=%s'%doc.text_upload)
            doc.save()
    
    def log_auto(self, request, doc, message):
        '''Keep a record of what automatic tasks have been done.'''
        u = request.user
        now = datetime.now()
        doc.auto_log += '\n>--->user=%s,when=%s'%(u, now)
        doc.auto_log += '\n%s<---<'%message
        doc.date_last_auto = now
       
    # ---------------------------------------------------------------
    # Set the text via a URL.
    # ---------------------------------------------------------------
    def auto_get_text(self, request, doc):
        '''Load the text field from a website.'''
        messages.warning(request, 'Trying to get text from a URL.') 
        
        if doc.auto_get_url:
            messages.warning(request, 'URL: %s'%doc.auto_get_url)
            messages.error(request, 'HAVE YOU CHECKED IT WORKS AND IS SAFE?')    
        else:
            messages.error(request, "Field 'Auto get url' does not contain a URL.")
            return False
        content = self.get_page(request, doc.auto_get_url)
        
        if content:
            doc.text = content
            doc.auto_get_enabled = False
            if doc.status == 5:
                doc.status = 7
                m = 'Status changed from Public to Hidden, do a visual check.'
                messages.warning(request, m)
            self.log_auto(request, doc, 'autogeturl=%s'%doc.auto_get_url)
            doc.save() 
            messages.success(request, 'Text from url loaded and saved.')
    
    def get_page(self, request, url):
        '''Return the contents of the URL or False if it fails.'''
        try:
            response = urllib2.urlopen(url)
        except ValueError:
            m = 'You URL is probably missing the resource type. e.g. http://'
            messages.error(request, m)
            return False
        except URLError as e:
            messages.error(request, 'Fetch failed for the following reason.')
            messages.error(request, e)
            return False
        return response.read()
    
    # ---------------------------------------------------------------
    # Set the html field automatically from the text field
    # ---------------------------------------------------------------
    def html_auto(self, request, doc):
        '''Use text field to make documents in html.'''
        messages.warning(request, 'Please wait, trying to create html.')
        if doc.text:
            # Find out how the text will be converted and suboptions.
            try:
                key = doc.format
                if key == None:
                    m = 'hauto41: The format for the document has not been set.'
                    messages.error(request, m)
                    return False
                f = Format.objects.get(pk=key)
                enabled = f.html_convert_enable
                how = f.html_convert_method
                opts = f.html_convert_options
            except Format.DoesNotExist:
                m = 'hauto42: The format picked is missing vital information.'
                messages.error(request, m)
                m = 'hauto43: Format missing: %s'%key
                messages.info(request, m)
                enabled = False
                
            # Before doing the task.
            if enabled:
                self.do_html(request, doc, how, opts)

    def do_html(self, request, doc, how, opts):
        '''Controls how the html is made and with which options.'''                       
        if not how: how = 'pygments' # enable a default option
        use = DoHtml()
        if how == 'pygments':
            content = use.do_pygments(request, doc, opts)
        elif how == 'hdemo1':
            content = use.do_hdemo1(request, doc, opts)
        elif how == 'hxslt':
            content = use.do_hxslt(request, doc, opts)
        else:
            m = 'hauto51: Format has invalid html convert method.' 
            messages.error(request, m)
            content = '' #Make sure content is defined or it causes error.
        
        # Now we can save the content
        if content:
            doc.html_auto_doc = content
            doc.html_auto_enabled = False
            self.log_auto(request, doc, 'autohtmlhow=%s'%how)
            doc.save()
            m = 'Finished, the HTML was created and saved.'
            messages.success(request, m)
        else:
            m = 'hauto52: Create HTML processed but produced nothing.'
            messages.error(request, m)
            m = 'hauto53: Method tried (%s) with options(%s)'%(how, opts)
            messages.warning(request, m)

admin.site.register(Document, DocumentAdmin)

    