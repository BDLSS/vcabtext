from django.conf.urls.defaults import patterns, url

from vocabdj.vdata import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<document_id>\d+)/$', views.detail, name='detail'),
)
