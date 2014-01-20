# This file is used to test ideas.
#
# 1. Checking how pygments works and what lexers are available.
# 2. Checking how lxml transforms documents.
#
# To use this on servers you need to install both. It is possible that
# the pygments library is already installed on some linux desktops.
#
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles

def get_styles():
    # Grab all the possible styles
    # The idea of this came from a website, link lost.
    styles = list(get_all_styles())
    
    print("\nAll built in styles for Pygments: ")
    for style in styles:
        print('- ' + style)
    
    # Enter name of style from the above list.
    pick_style = raw_input('\nEnter name of chosen style: ')
    
    # Check user input is a valid style
    while pick_style not in styles:
        print('A Style with that name does not exist. Please try again.')
        pick_style = raw_input('\nEnter name of chosen style: ')       
    else:
        # If valid then create the CSS file
        
        style = HtmlFormatter(style=pick_style).get_style_defs('.highlight')
        print style
        
        print('Style successfully generated.')
        
def get_lexers():
    ''''''
    import pygments.lexers as t
    count = 0 
    for item in t.get_all_lexers():
        print item
        count += 1
    try:
        print t.get_lexer_for_filename('this.xsd')
    except:
        print 'found'
    print 'NUMBER OF LEXERS: %s'%count

def rdf_maker():
    '''Test how to convert rdf using xslt'''
    import StringIO
    #Example from http://www.w3schools.com/rdf/rdf_example.asp
    rdf = StringIO.StringIO("""<?xml version="1.0"?>

<rdf:RDF
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns:cd="http://www.recshop.fake/cd#">

<rdf:Description
rdf:about="http://www.recshop.fake/cd/Empire Burlesque">
  <cd:artist>Bob Dylan</cd:artist>
  <cd:country>USA</cd:country>
  <cd:company>Columbia</cd:company>
  <cd:price>10.90</cd:price>
  <cd:year>1985</cd:year>
</rdf:Description>

<rdf:Description
rdf:about="http://www.recshop.fake/cd/Hide your heart">
  <cd:artist>Bonnie Tyler</cd:artist>
  <cd:country>UK</cd:country>
  <cd:company>CBS Records</cd:company>
  <cd:price>9.90</cd:price>
  <cd:year>1988</cd:year>
</rdf:Description>
</rdf:RDF>
""")
    
    from lxml import etree
    doc = etree.parse(rdf)
        
    xslt_root = etree.XML('''<xsl:stylesheet version="1.0"
     xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
     <xsl:template match="/">
If you are reading this <eggs><xsl:value-of select="/a/b/text()" /></eggs>
it WORKS1.
     </xsl:template>
it WORKS2.
 </xsl:stylesheet>''')
    
    try:
        transform = etree.XSLT(xslt_root)
        content = transform(doc)
        print content
    except etree.Error, e:
        print 'ERROR:  %s'%e
    
    
    

#get_styles()
get_lexers()
print '-'*10
rdf_maker()
