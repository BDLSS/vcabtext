from django.contrib import admin
from vdata.models import Format, Collection, Document

ENABLE_FIELDSETS = True

class FormatAdmin(admin.ModelAdmin):
    list_display = ('format', 'expanded_acronym', 'html_convert_enable', 'native_mime_type')
    

admin.site.register(Format, FormatAdmin)


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('collection', 'longer_name')

admin.site.register(Collection, CollectionAdmin)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'namespace')
    list_filter = ('collection','format')
    
    if ENABLE_FIELDSETS:
        fieldsets = (
                        (None, {'fields':
                              ('name', 'namespace', 'format',
                               'collection', 'brief_description')
                              }),
                      
                        ('Less used general fields', {
                            'classes': ('collapse', 'wide', 'extrapretty'),
                            'description': 'If general fields are used less often they can appear here.',
                            'fields': ('home_url',
                                       'home_doc_url',
                                       'description',
                                       'notes'),
                              }),
                      
                        ('Document contents', {
                            'classes': ('wide', 'extrapretty'),
                            'description': 'These are the raw text send to users.',
                            'fields': ('text',
                                       'html_enabled',
                                       'html_doc'),
                              }),
                     
                        ('Auto text options', {
                            'classes': ('wide', 'extrapretty', 'collapse'),
                            'description': 'These fields can automatically update the text field. (To be implemented)',
                            'fields': ('text_fetch_enabled',
                                       'compress_start_doc',
                                       'compress_includes_auto_add'),
                              }),
                     
                        ('Version linkage', {
                            'classes': ('wide', 'extrapretty', 'collapse'),
                            'description': 'These fields let you make links between documents.',
                            'fields': ('version_current',
                                       'version_previous',
                                       'version_next',
                                       'version_extends',
                                       'version_parent',),
                              }),
                      )

admin.site.register(Document, DocumentAdmin)

    