from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'potty.views.bathrooms', name='bathrooms'),
    url(r'^bathroom/(?P<bathroom_id>\d+)/?$', 'potty.views.bathroom', name='bathroom'),
    url(r'^bathroom/create/?$', 'potty.views.create', name='create'),
    url(r'^bathroom/(?P<bathroom_id>\d+)/lock/?$', 'potty.views.lock', name='lock'),
    url(r'^bathroom/(?P<bathroom_id>\d+)/unlock/?$', 'potty.views.unlock', name='unlock'),
    url(r'^bathroom/(?P<bathroom_id>\d+)/status/?$', 'potty.views.status', name='status'),
)
