# This module deals with automatically creating html documentation
# for a given item within vocab.
#
# It gets called via an a save_model in the admin form.
#

from django.contrib import messages
from vdata.models import Document

try:
    from pygments import highlight
    from pygments.lexers import XmlLexer, XsltLexer, TextLexer
    from pygments.lexers import get_lexer_for_filename
    from pygments.formatters import HtmlFormatter
        
    ENABLE_PYGMENTS = True
except ImportError:
    ENABLE_PYGMENTS = False
                
ENABLE_FIELDSETS = True

# The following are need by the hxslt convert method
try:
    from StringIO import StringIO
    from lxml import etree
    ENABLE_HXSLT = True
except ImportError:
    ENABLE_HXSLT = False

class DoHtml(object):
    def do_pygments(self, request, doc, options):
        '''Use pygments to create and save the html text.'''
        if not ENABLE_PYGMENTS:
            m = 'hauto60: Library needed for pygments is not available.'
            messages.error(request, m)
            return ''
        if not options: options = 'xml, linenos' #defaults
        custom = options.split(',')
        
        # The first option sets the lexer to use. For available
        # lexers goto http://pygments.org/docs/lexers/
        if custom[0] == 'xml': 
            lexer = XmlLexer
        elif custom[0] == 'xslt': 
            lexer = XsltLexer
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
    def do_hxslt(self, request, doc, options):
        '''Try to create an html version for an RDF file using an XSLT.'''
        if not ENABLE_HXSLT:
            m = 'hauto51: The library needed for hxslt is not available.' 
            messages.error(request, m)
            return ''
                
        try:
            docid = options[0]
        except IndexError:
            m = 'Hxslt21: The format is missing the xslt document id to look for.'
            messages.error(request, m)
            return ''
                
        before = doc.text
        content = self.do_hxslt_content(request, before, docid) 
        if content == '':
            m = 'Hxslt26: Nothing was produced, using the default method.'
            messages.info(request, m)
            content = self.do_pygments(request, doc, [])
        
        # A simple method of reporting if anything occurred
        #m = 'Size before=%s, Size after=%s'%(len(before), len(content))
        #messages.info(request, m)
        
        return content # return the new content
    
    def do_hxslt_content(self, request, raw, xslt_id):
        '''Return the rdf document as html source code.'''
        rdf = StringIO(raw)
        source = etree.parse(rdf)
        xstree = self.get_xslt_tree(request, xslt_id)
        try:
            transform = etree.XSLT(xstree)
            return str(transform(source))
        except etree.Error, e:
            m = 'Hxslt25: Unable to transform file, the hint might explain why.'
            messages.warning(request, m)
            m = 'Hint: %s'%e
            messages.error(request, m)
            return ''
        
    def get_xslt_tree(self, request, doc_id):
        '''Return the XSLT tree to use to convert from RDF.'''
        try:
            doc = Document.objects.get(pk=doc_id)
            #messages.warning(request, str(doc))
        except Document.DoesNotExist:
            m = 'Hxslt22: The document id containing the XSLT cannot be found.'
            messages.error(request, m)
        try:
            return etree.XML(doc.text)
        except ValueError:
            m = 'Hxslt23: The XSLT raised a value error. (encodings)' 
            messages.warning(request, m)
            m = 'Hxslt24: The default is being used.' 
            messages.info(request, m)
            return etree.XML('''<xsl:stylesheet version="1.0"
     xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
     <xsl:template match="/">
     <xsl:copy-of select="."/>
     </xsl:template>
 </xsl:stylesheet>''')
            