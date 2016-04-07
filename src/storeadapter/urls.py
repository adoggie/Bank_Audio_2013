from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
import webapi


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tax.views.home', name='home'),
    # url(r'^tax/', include('tax.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
	url(r'^login',webapi.login),
	url(r'^updateTermInfo',webapi.updateTermInfo),
	url(r'^getTermInfo',webapi.getTermInfo),
	url(r'^syncPrepare',webapi.syncPrepare),
	url(r'^syncFile',webapi.syncFile),
	url(r'^getCurrentVersion',webapi.getCurrentVersion),
	url(r'^downloadSetupPackage',webapi.downloadSetupPackage),
	url(r'^getClientInfoList',webapi.getClientInfoList),
	url(r'^uploadClientInfoList',webapi.uploadClientInfoList),
	url(r'^getClientInfoList',webapi.getClientInfoList),
	url(r'^updateAudioMemo',webapi.updateAudioMemo),

	
)
