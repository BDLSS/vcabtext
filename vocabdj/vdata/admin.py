from django.contrib import admin, messages
from vdata.models import Format, Collection, Document, Tag, Category
from urllib2 import URLError
from datetime import datetime

try:
    from pygments import highlight
    from pygments.lexers import XmlLexer
    from pygments.formatters import HtmlFormatter
    ENABLE_AUTO_HTML = True
except ImportError:
    ENABLE_AUTO_HTML = False
            
ENABLE_FIELDSETS = True

import urllib2

class FormatAdmin(admin.ModelAdmin):
    list_display = ('format', 'expanded_acronym', 'html_convert_enable', 'native_mime_type')
    
admin.site.register(Format, FormatAdmin)


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('collection', 'longer_name')

admin.site.register(Collection, CollectionAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'notes')

admin.site.register(Tag, TagAdmin)

class CatAdmin(admin.ModelAdmin):
    list_display = ('category', 'notes')

admin.site.register(Category, CatAdmin)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'format', 'collection', 'maintainer')
    list_display_links = ('id', 'name')
    list_filter = ('date_modified', 'status', 'maintainer', 'collection')
    date_hierarchy = 'date_document'
    readonly_fields = ('date_added', 'date_modified', 'date_last_auto', 'auto_log')
    filter_horizontal = ('categories', 'tags')
    
    raw_id_fields = ('version_extends','version_parent', 'version_related', 'version_previous', 'version_next')
    
    if ENABLE_FIELDSETS:
        hide = ('collapse', 'wide', 'extrapretty')
        fieldsets = (
                        (None, {'fields': ('name',  )}),
                        
                        ('Important details', {
                              'classes': hide,
                              'description': 'These fields are needed by many non-admin page.',
                              'fields':
                              ('brief_description', 'format', 'collection',
                                    'maintainer', 'text')
                              }),
                      
                        ('More details', {
                            'classes': hide,
                            'description': 'If general fields are used less often they can be moved here.',
                            'fields': ('source',
                                       'suggested_namespace',
                                       'creators',
                                       'contributors',
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
                     
                        ('Categories and Tags', {
                            'classes': hide,
                            'description': 'You can assign categories and tags if you wish.',
                            'fields': ('categories',
                                       'tags',
                                       ),
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
                     
                        ('Admin options', {
                            'classes': hide,
                            'description': 'These fields are for use by library staff mainly.',
                            'fields': ('status',
                                       'date_added',
                                       'date_modified',
                                       'date_last_auto',
                                       'auto_log',
                                       ),
                              }),
                     
                      )

    # ---------------------------------------------------------------
    # Custom save handler and best method of fetching text.
    # ---------------------------------------------------------------
    def save_model(self, request, doc, form, change):
        '''Add custom save options to admin.'''
        doc.save() # Save the model first to deal with any errors.
                
        # Enable the setting of the text field via file upload.
        if doc.text_fetch_enabled: # This has more priority
            self.text_fetch(request, doc)
        else:
            # Enable the setting of the text field via a url.
            if doc.auto_get_enabled: # This has less priority
                self.auto_get_text(request, doc)
                
        # Enable the setting of the html field via text.
        if ENABLE_AUTO_HTML and doc.html_auto_enabled:
            self.html_auto(request, doc)
                
    def text_fetch(self, request, doc):
        '''Load the text field from the uploaded filed.'''
        messages.warning(request, 'Trying to set text from uploaded file.')
        uploaded = doc.text_upload # this contains the file information
        if uploaded:
            doc.text = uploaded.read()
            messages.success(request, 'Text successfully loaded.')
            doc.text_fetch_enabled = False
            self.log_auto(request, doc, 'file=%s'%'fa')
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
        messages.warning(request, 'Trying to automatically create html.')
        if doc.text:
            # Find out how the text will be converted and suboptions.
            try:
                key = doc.format
                if key == None:
                    m = 'You forgot to set the format for this document.'
                    messages.error(request, m)
                    return False
                f = Format.objects.get(pk=key)
                enabled = f.html_convert_enable
                how = f.html_convert_method
                opts = f.html_convert_options
            except Format.DoesNotExist:
                messages.error(request, 'Format information is missing, auto html not available.')
                enabled = False
            # Before doing the task.
            if enabled:
                self.do_html(request, doc, how, opts)

    def do_html(self, request, doc, how, opts):
        '''Controls how the html is made and with which options.'''                        
        if not how: how = 'pygments' # enable a default option
        if how == 'pygments':
            self.do_pygments(request, doc, opts)
        else:
            messages.error(request, 'Format has invalid html convert method.')

    def do_pygments(self, request, doc, options):
        '''Use pygments to create and save the html text.'''
        if not options: options = 'xml, linenos' #defaults
        custom = options.split(',')
        
        # The first option sets the lexer to use. For available
        # lexers goto http://pygments.org/docs/lexers/
        if custom[0] == 'xml': 
            lexer = XmlLexer
        elif custom[0] == 'xslt': 
            lexer = XmlLexer # TODO: get xslt to works
        elif custom[0] == 'json': 
            lexer = XmlLexer # TODO: get json to works.
        
        # The second controls if line number be shown on the output?
        has_num = False
        if len(custom)> 1 and str(custom[1]).strip() == 'linenos':
            has_num = 'inline'
        
        # Now we can do the task and save it.
        content = highlight(doc.text, lexer(), HtmlFormatter(linenos=has_num))  
        doc.html_auto_doc = content
        messages.success(request, 'HTML successfully created.')
        doc.html_auto_enabled = False
        doc.save()
        
admin.site.register(Document, DocumentAdmin)

    