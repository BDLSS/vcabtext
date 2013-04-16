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
    list_display = ('id', 'name', 'maintainer', 'format', 'source', 'status')
    list_filter = ('date_modified', 'status', 'maintainer', 'collection')
    date_hierarchy = 'date_modified'
    
    raw_id_fields = ('version_extends','version_parent', 'version_related', 'version_previous', 'version_next')
    
    if ENABLE_FIELDSETS:
        hide = ('collapse', 'wide', 'extrapretty')
        fieldsets = (
                        (None, {'fields': ('name', )}),
                        
                        ('Important details', {
                              'classes': hide,
                              'description': 'These fields are needed by many non-admin page.',
                              'fields':
                              ('format', 'collection',
                                    'brief_description', 'maintainer', 'text')
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
                            'fields': ('text_fetch_enabled',
                                       'compress_start_doc',
                                       'compress_includes_auto_add'),
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
                                       ),
                              }),
                     
                      )

admin.site.register(Document, DocumentAdmin)

    