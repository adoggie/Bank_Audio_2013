from django.conf.urls import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from audio import views,org_views,user_views,terminal_views,archive_views,client_views,account,statistics_views

urlpatterns = patterns('',
	url(r'login/$', account.login,name="login"),
	url(r'dialogLogin/$', account.dialoglogin,name="dialogLogin"),
	url(r'logout/$', account.logout,name="logout"),
	url(r'change_password/$', account.change_password,name="change_password"),
	url(r'index/$', views.index,name="index"),
	url(r'get_org_tree_json/$', account.get_org_tree_json,name="get_org_tree_json"),
	url(r'get_org_tree_json2/$', account.get_org_tree_json2,name="get_org_tree_json2"),
	url(r'testnavTab/$', views.testnavTab,name="testnavTab"),
#	url(r'terminal_search/$', terminal_views.terminal_list,name="terminal_search"),
#	url(r'terminal_add/$', terminal_views.terminal_add,name="terminal_add"),
#	url(r'terminal_delete/$', terminal_views.terminal_delete,name="terminal_delete"),
)


urlpatterns += patterns('',
	url(r'ztreetest/$', views.ztreetest,name="ztreetest"),
	url(r'test/$', views.test,name="test"),
	url(r'organization/$', org_views.organization,name="organization"),
	url(r'org_list/$', org_views.org_list,name="org_list"),
	url(r'get_org_objs/$', org_views.get_org_objs,name="get_org_objs"),
	url(r'org_add/$', org_views.org_add,name="org_add"),
	url(r'org_delete/$', org_views.org_delete,name="org_delete"),
	url(r'org_deletemany/$', org_views.org_deletemany,name="org_deletemany"),
	url(r'org_search/$', org_views.org_list,name="org_search"),
	url(r'orgs_export/$', org_views.orgs_export,name="orgs_export"),
)
urlpatterns += patterns('',
	url(r'user/$', user_views.user,name="user"),
#	url(r'get_org_tree_json/$', user_views.get_org_tree_json,name="get_user_tree_json"),
	url(r'user_list/$', user_views.user_list,name="user_list"),
#	url(r'get_user_objs/$', user_views.get_user_objs,name="get_user_objs"),
	url(r'user_add/$', user_views.user_add,name="user_add"),
	url(r'user_delete/$', user_views.user_delete,name="user_delete"),
#	url(r'user_deletemany/$', user_views.user_deletemany,name="user_deletemany"),
	url(r'user_search/$', user_views.user_list,name="user_search"),
	url(r'users_export/$', user_views.users_export,name="users_export"),
)
urlpatterns += patterns('',
	url(r'terminal/$', terminal_views.terminal,name="terminal"),
	url(r'terminal_list/$', terminal_views.terminal_list,name="terminal_list"),
	url(r'terminal_search/$', terminal_views.terminal_list,name="terminal_search"),
	url(r'terminal_add/$', terminal_views.terminal_add,name="terminal_add"),
	url(r'terminal_delete/$', terminal_views.terminal_delete,name="terminal_delete"),
	url(r'get_belong_terminal2/$', terminal_views.get_belong_terminal2,name="get_belong_terminal2"),
	url(r'terminals_export/$', terminal_views.terminals_export,name="terminals_export"),
)

urlpatterns += patterns('',
	url(r'client/$', client_views.client,name="client"),
	url(r'client_list/$', client_views.client_list,name="client_list"),
	url(r'client_search/$', client_views.client_list,name="client_search"),
	url(r'client_add/$', client_views.client_add,name="client_add"),
	url(r'client_delete/$', client_views.client_delete,name="client_delete"),
	url(r'clients_export/$', client_views.clients_export,name="clients_export"),
)

urlpatterns += patterns('',
	url(r'archive/$', archive_views.archive,name="archive"),
	url(r'archive_list/$', archive_views.archive_list,name="archive_list"),
	url(r'archive_search/$', archive_views.archive_list,name="archive_search"),
	url(r'archive_add/$', archive_views.archive_add,name="archive_add"),
	url(r'archive_delete/$', archive_views.archive_delete,name="archive_delete"),
	url(r'archive_play/$', archive_views.archive_play,name="archive_play"),
	url(r'archive_download/$', archive_views.archive_download,name="archive_download"),
	url(r'archive_deletemany/$', archive_views.archive_deletemany,name="archive_deletemany"),
	url(r'archieve_deleteFilter/$', archive_views.archieve_deleteFilter,name="archieve_deleteFilter"),
	url(r'archieves_export/$', archive_views.archieves_export,name="archieves_export"),

#	url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),

)

urlpatterns += patterns('',
	url(r'manager_statistics/$', statistics_views.manager_statistics,name="manager_statistics"),
	url(r'mana_statis_list/$', statistics_views.mana_statis_list,name="mana_statis_list"),
	url(r'mana_statis_search/$', statistics_views.mana_statis_list,name="mana_statis_search"),
	url(r'mana_statis_export/$', statistics_views.mana_statis_export,name="mana_statis_export"),

	url(r'client_statistics/$', statistics_views.client_statistics,name="client_statistics"),
	url(r'client_statis_list/$', statistics_views.client_statis_list,name="client_statis_list"),
	url(r'client_statis_search/$', statistics_views.client_statis_list,name="client_statis_search"),
	url(r'client_statis_export/$', statistics_views.client_statis_export,name="client_statis_export"),
)
if settings.DEBUG == True:
	urlpatterns += patterns('',
		url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
	)

urlpatterns += patterns('',
	url(r'$', account.login),
)


