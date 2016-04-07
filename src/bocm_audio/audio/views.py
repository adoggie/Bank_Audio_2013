__author__ = 'daitr'
#-*-coding:utf-8-*-

import traceback,os
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.template import Context,RequestContext
from django.shortcuts import render_to_response

from audio.constants import STATUS_CODE
from utils.pageHandle import getPage
from audio.account import *
from audio.models import *
from utils.MyEncoder import getJson
from utils.parseConfig import getConfigValue
from django.conf import settings
from django.views.generic import TemplateView

import logging
log = logging.getLogger('audio_logger')

def _getServerInfo():
	'''
		added 2013.6.12 scott
	'''
	import storeadapter.utils
	import storeadapter.base

	all,used = storeadapter.utils.get_disk_space(storeadapter.base.STORE_DIR)
	all = float(all)

	pattern=u"磁盘总空间:%s G <br/>"\
	        u"磁盘剩余空间:%s G<br/>"\
	        u"磁盘利用率:%s %%<br/>"
	#,其中录音资料占用:%s G<br />"\
	per = round(used/all,2)*100
	result = pattern%(all,all-used,int(per))
	return result

def test(request):
	print request
	return render_to_response("test.html")
#	return HttpResponse('abc')
#	log.info("test")
#	a_rawset = Archive.objects.raw('SELECT count(*) as aaa FROM audio_client')
#	for a in a_rawset:
#		print type(a.aaa)
#	list = a_rawset
#	return render_to_response("testplayArchive.html")
#	return render_to_response("standardData.html")

def ztreetest(request):
	return render_to_response("ztreetest.html")

@csrf_exempt
def testnavTab(request):
	if request.method =="POST":
		name = request.POST.get("name","")
	return render_to_response("demo_page1.html",{},context_instance=RequestContext(request))


@requires_login
def index(request):
	user = request.session.get("user")
	company =""
	tel = ""
	version =""
	try:
		configPath = os.path.join(settings.CONFIG_DIR, 'foot.ini').replace('\\','/')
		company = getConfigValue(configPath,"foot",'company')
		tel = getConfigValue(configPath,"foot",'tel')
		version = getConfigValue(configPath,"foot",'version')
		serverinfo = _getServerInfo()
	except:
		traceback.print_exc()
		return
	context = Context({
		"user":user,
		"company":company,
		"tel":tel,
		"version":version,
		'serverinfo':serverinfo,
	})
	return render_to_response("index.html",context,context_instance=RequestContext(request))


class TestView(TemplateView):
	template_name = "test.html"
