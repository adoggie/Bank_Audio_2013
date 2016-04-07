__author__ = 'daitr'
#--coding:utf-8--
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
def responsenoPermission(request):
	if request.is_ajax():
		jsondata = {"statusCode":"300","message":u"对不起,您没有权限访问此网页!",}
		return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
	else:
		return render_to_response("noPermission.html")