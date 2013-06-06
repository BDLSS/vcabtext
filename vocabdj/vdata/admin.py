from django.contrib import admin, messages
from vdata.models import Format, Collection, Document, Tag, Category, Agent
from urllib2 import URLError
from datetime import datetime
from django.contrib import auth

try:
    from pygments import highlight
    from pygments.lexers import XmlLexer, JSONLexer, XsltLexer, TextLexer
    from pygments.lexers import get_lexer_for_filename
    from pygments.formatters import HtmlFormatter
    
    # The following are need by the rdfxslt convert method
    from StringIO import StringIO
    from lxml import etree
    
    ENABLE_AUTO_HTML = True
except ImportError:
    ENABLE_AUTO_HTML = False
                
ENABLE_FIELDSETS = True

import urllib2

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
        if how == 'pygments':
            content = self.do_pygments(request, doc, opts)
        elif how == 'hdemo1':
            content = self.do_hdemo1(request, doc, opts)
        elif how == 'rdfxslt':
            content = self.do_rdfxslt(request, doc, opts)
        else:
            m = 'hauto51: Format has invalid html convert method.' 
            messages.error(request, m)
        
        # Now we can save the content
        if content:
            doc.html_auto_doc = content
            doc.html_auto_enabled = False
            self.log_auto(request, doc, 'HTML auto updated.')
            doc.save()
            m = 'Finished, the HTML was created and saved.'
            messages.success(request, m)
        else:
            m = 'hauto52: Create HTML processed but produced nothing.'
            messages.error(request, m)
            m = 'hauto53: Method tried (%s) with options(%s)'%(how, opts)
            messages.warning(request, m)

    def do_pygments(self, request, doc, options):
        '''Use pygments to create and save the html text.'''
        if not options: options = 'xml, linenos' #defaults
        custom = options.split(',')
        
        # The first option sets the lexer to use. For available
        # lexers goto http://pygments.org/docs/lexers/
        if custom[0] == 'xml': 
            lexer = XmlLexer
        elif custom[0] == 'xslt': 
            lexer = XsltLexer
        elif custom[0] == 'json': 
            lexer = JSONLexer
        elif custom[0] == 'guess':
            lexer, example = self.pyg_guess(custom)
            m = 'hauto61: Lexer guessed:%s using example: %s'%(lexer, example)
            messages.info(request, m)
        else:
            lexer = TextLexer # Have a safe default if mistake made.  
        
        # The second controls if line number be shown on the output?
        has_num = False
        if len(custom)> 1 and str(custom[1]).strip() == 'linenos':
            has_num = 'inline'
        
        # Now we can do the task and save it.
        try:
            return highlight(doc.text, lexer(), HtmlFormatter(linenos=has_num))
        except TypeError: # this is caused by the guess feature
            try:
                return highlight(doc.text, lexer, HtmlFormatter(linenos=has_num))
            except: # TODO: what exceptions do lexer highlighter cause?
                return ''

    def pyg_guess(self, options):
        '''Try to guess the lexer to use.'''
        try:
            example = str(options[2]).strip()
        except IndexError:
            example = 'guess.txt'
        try:
            lexer = get_lexer_for_filename(example)
        except:
            lexer = TextLexer
        return lexer, example
                
    def do_hdemo1(self, request, doc, options):
        if not options: options = 'xml, linenos' #defaults
        
        before = doc.text # how to access the text to be converted
        content = str('DEMODONE'+before) # do your conversion method to create html 
        
        # A simple method of reporting if anything occurred
        m = 'Size before=%s, Size after=%s'%(len(before), len(content))
        messages.info(request, m)
        
        return content # return the new content
    
    # ---------------------------------------------------------------
    # Set the html field automatically for an RDF file
    # ---------------------------------------------------------------
    def do_rdfxslt(self, request, doc, options):
        '''Try to create an html version for an RDF file using an XSLT.'''
        try:
            docid = options[0]
        except IndexError:
            m = 'Rdfxslt21: The format is missing the xslt document id to look for.'
            messages.error(request, m)
            return ''
                
        before = doc.text
        content = self.do_rd2xs_content(request, before, docid) 
        if content == '':
            m = 'Rdfxslt26: Nothing was produced, using the default method.'
            messages.info(request, m)
            content = self.do_pygments(request, doc, [])
        
        # A simple method of reporting if anything occurred
        #m = 'Size before=%s, Size after=%s'%(len(before), len(content))
        #messages.info(request, m)
        
        return content # return the new content
    
    def do_rd2xs_content(self, request, raw, xslt_id):
        '''Return the rdf document as html source code.'''
        rdf = StringIO(raw)
        source = etree.parse(rdf)
        xstree = self.rdf_xslt_tree(request, xslt_id)
        try:
            transform = etree.XSLT(xstree)
            return str(transform(source))
        except etree.Error, e:
            m = 'Rdfxslt25: Unable to transform file, the hint might explain why.'
            messages.warning(request, m)
            m = 'Hint: %s'%e
            messages.error(request, m)
            return ''
        
    def rdf_xslt_tree(self, request, doc_id):
        '''Return the XSLT tree to use to convert from RDF.'''
        try:
            doc = Document.objects.get(pk=doc_id)
            #messages.warning(request, str(doc))
        except Document.DoesNotExist:
            m = 'Rdfxslt22: The document id containing the XSLT cannot be found.'
            messages.error(request, m)
        try:
            return etree.XML(doc.text)
        except ValueError:
            m = 'Rdfxslt23: The XSLT raised a value error. (encodings)' 
            messages.warning(request, m)
            m = 'Rdfxslt24: The default is being used.' 
            messages.info(request, m)
            return etree.XML('''<xsl:stylesheet version="1.0"
     xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
     <xsl:template match="/">
     <xsl:copy-of select="."/>
     </xsl:template>
 </xsl:stylesheet>''')
          
admin.site.register(Document, DocumentAdmin)

    