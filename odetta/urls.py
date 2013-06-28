from django.conf.urls import patterns, include, url
from odetta.views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', home_page),
    url(r'^plot/(\d+)/img/$', plot_mid),
    url(r'^plot/(?P<id>\d+)/$', plot),
    url(r'^ajax/plot/(?P<id>\d+)/(?P<frame>\d+)/$', get_all_data),
    url(r'^plot_few/(\d+)/$', plot_few),
    url(r'^text/$', text),
    url(r'^search/$', search_models),
    url(r'^about/$', about),
    url(r'^fitter/$', fitter),
    # Examples:
    #url(r'^$', 'odetta.views.home', name='home'),
    #url(r'^odetta/', include('odetta.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
