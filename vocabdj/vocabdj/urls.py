from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from vdata import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'vocabdj.views.home', name='home'),
    # url(r'^vocabdj/', include('vocabdj.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
     url(r'^data/', include('vdata.urls')),
     url(r'^/', include('django.contrib.flatpages.urls')),
     
     # These urls are are duplicated from inside the application.
     url(r'^(?P<document_name>.+)/current/$', views.download_latest, name='docname'),
     url(r'^(?P<doc_name>.+)/(?P<doc_version>.+)/info/$', views.version_info, name='versioninfo'),
     url(r'^(?P<doc_name>.+)/(?P<doc_version>.+)/$', views.download_version, name='docversion'), 
)
