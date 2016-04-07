from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bocm_audio.views.home', name='home'),
    # url(r'^bocm_audio/', include('bocm_audio.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)




urlpatterns += patterns('',
	url(r'^WebApi/Terminal/',include('storeadapter.urls')),
	#url(r'^WebApi/Terminal/',include('audio.urls')),
    url(r'^',include('audio.urls')),
)