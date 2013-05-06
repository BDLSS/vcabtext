from django.contrib import admin, messages
from vdata.models import Format, Collection, Document, Tag, Category

try:
    from pygments import highlight
    from pygments.lexers import XmlLexer
    from pygments.formatters import HtmlFormatter
    ENABLE_AUTO_HTML = True
except ImportError:
    ENABLE_AUTO_HTML = False
            
ENABLE_FIELDSETS = True

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
    list_display = ('id', 'name', 'maintainer', 'format', 'source', 'status')
    list_display_links = ('id', 'name')
    list_filter = ('date_modified', 'status', 'maintainer', 'collection')
    date_hierarchy = 'date_document'
    readonly_fields = ('date_added', 'date_modified')
    filter_horizontal = ('categories', 'tags')
    
    raw_id_fields = ('version_extends','version_parent', 'version_related', 'version_previous', 'version_next')
    
    if ENABLE_FIELDSETS:
        hide = ('collapse', 'wide', 'extrapretty')
        fieldsets = (
                        (None, {'fields': ('name', 'brief_description' )}),
                        
                        ('Important details', {
                              'classes': hide,
                              'description': 'These fields are needed by many non-admin page.',
                              'fields':
                              ('format', 'collection',
                                    'maintainer', 'text')
                              }),
                      
                        ('Descriptors', {
                            'classes': hide,
                            'description': 'If general fields are used less often they can appear here.',
                            'fields': ('description',
                                       'source',
                                       'suggested_namespace',
                                       'namespace_uri',
                                       'home_doc_url',
                                       'creators',
                                       'contributors',
                                       'notes'),
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
                            'description': 'These fields can automatically update the text field. (To be implemented)',
                            'fields': ('text_upload',
                                       'text_fetch_enabled',
                                       'compress_start_doc',
                                       'compress_includes_auto_add',
                                       'compress_upload')
                              }),
                     
                        ('Version linkage', {
                            'classes': hide,
                            'description': 'These fields let you make links between documents.',
                            'fields': ('version_current',
                                       'version_extends',
                                       'version_parent',
                                       'version_related',
                                       'version_previous',
                                       'version_next'),
                              }),
                     
                        ('Admin options', {
                            'classes': hide,
                            'description': 'These fields are for use by library staff mainly.',
                            'fields': ('status',
                                       'date_document',
                                       'date_added',
                                       'date_modified',
                                       ),
                              }),
                     
                      )

    def save_model(self, request, doc, form, change):
        '''Add custom save options to admin.'''
        doc.save() # Save the model first to deal with any errors.
        
        # Enable the setting of the text field via file upload.
        if doc.text_fetch_enabled:
            self.text_fetch(request, doc)
                
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
            doc.save()
    
    def html_auto(self, request, doc):
        '''Use text field to make documents in html.'''
        messages.warning(request, 'Trying to automatically create html.')
        if doc.text:
            # Find out how the text will be converted and suboptions.
            try:
                f = Format.objects.get(pk=doc.format)
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
        
        content = highlight(doc.text, lexer(), HtmlFormatter(linenos=has_num))  
        doc.html_auto_doc = content
        messages.success(request, 'HTML successfully created.')
        doc.html_auto_enabled = False
        doc.save()
        
admin.site.register(Document, DocumentAdmin)

    