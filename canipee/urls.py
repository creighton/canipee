from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.auth.views import login, logout
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'canipee.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # existing patterns here...
    (r'^accounts/login/$',  login),
    (r'^accounts/logout/$', logout),
    url(r'^accounts/register$', 'canipee.views.register', name='register'),
    url(r'^accounts/profile$', 'canipee.views.profile', name='profile'),

)
