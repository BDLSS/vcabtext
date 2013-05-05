from django.contrib import admin
from vdata.models import Format, Collection, Document, Tag, Category

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

    def save_model(self, request, obj, form, change):
        '''Add custom save options to admin.'''
        obj.save() # Save the model first to deal with any errors.
        log = str()
        
        # Enable the setting of the text field via file upload.
        if obj.text_fetch_enabled:
            log += 'Auto text option used by username: %s\n'%request.user
            uploaded = obj.text_upload # this contains the file information
            if uploaded:
                obj.text = uploaded.read()
                log += 'The file uploaded was: %s\n'%uploaded
            obj.text_fetch_enabled = False
        
        # Log our custom changes and save them.
        if log:
            obj.notes += log
        obj.save()
        
        
admin.site.register(Document, DocumentAdmin)

    