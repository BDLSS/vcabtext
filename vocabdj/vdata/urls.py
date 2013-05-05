from django.conf.urls.defaults import patterns, url

from vocabdj.vdata import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<document_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<document_id>\d+)/native/$', views.native, name='native'),
    url(r'^(?P<document_id>\d+)/web/$', views.web, name='web'),
    url(r'^(?P<document_id>\d+)/download/$', views.download, name='down'),
    url(r'^collects/$', views.collections, name='collects'),
)
