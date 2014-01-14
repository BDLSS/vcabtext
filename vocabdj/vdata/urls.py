from django.conf.urls import patterns, url

from vdata import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^perpage/(?P<pag_count>\d+)$', views.index, name='index_pag'),
    url(r'^(?P<document_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<document_id>\d+)/native/$', views.native, name='native'),
    url(r'^(?P<document_id>\d+)/web/$', views.web, name='web'),
    url(r'^(?P<document_id>\d+)/download/$', views.download, name='down'),
    url(r'^collects/$', views.collections, name='collects'),
    url(r'^collects/(?P<collection_collection>.+)/$', views.collection, name='collect'),
    url(r'^compact/$', views.compact, name='compact'),
    url(r'^(?P<document_name>.+)/current/$', views.download_latest, name='docname'),
    url(r'^(?P<document_name>.+)/current/info/$', views.current_info, name='curinfo'),
    url(r'^(?P<doc_name>.+)/(?P<doc_version>.+)/info/$', views.version_info, name='versioninfo'),
    url(r'^(?P<doc_name>.+)/(?P<doc_version>.+)/$', views.download_version, name='docversion'),
    url(r'^(?P<doc_name>.+)/$', views.content_neg, name='contentneg'),
)
