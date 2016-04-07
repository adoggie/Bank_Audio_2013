__author__ = 'daitr'
#-*-coding:utf-8-*-

import traceback
from django.http import HttpResponseRedirect,Http404,HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.template import Context,RequestContext
from django.db.models import Q
from django.views.decorators.cache import never_cache
import datetime
from utils import response

from audio.constants import STATUS_CODE
from utils.pageHandle import getPage


from audio.models import *
from utils.MyEncoder import getJson

import logging
log = logging.getLogger('audio_logger')

def _getServerInfo():
	'''
		added 2013.6.12 scott
	'''
	pattern=u"磁盘总空间:%s<br>" \
			u"磁盘剩余空间:%s,其中录音资料占用:15G" \
			u"磁盘利用率:%s"
	result = pattern%(0,0,0)
	return result



@csrf_exempt
def login(request):
	"""login the system"""
	try:
		user = request.session.get('user')
		if checkLogin(user):
			return HttpResponseRedirect("/index/")
		if request.method == "POST":
			#验证用户名和密码
			context = Context({})
			error=""
			try:
				username = request.POST.get("username")
				password = request.POST.get("password")
				if username:
					try:
						userinfo = User.objects.get(user = username)
					except User.DoesNotExist,e:
						error =u"用户与密码不匹配!"
						context.update({"error":error})
						return render_to_response("login.html",context,context_instance= RequestContext(request))
					except User.MultipleObjectsReturned,e:
						error =u"用户错误!"
						context.update({"error":error})
						return render_to_response("login.html",context,context_instance= RequestContext(request))
					else:
						if password == userinfo.passwd:
#							try:
#								del request.session['user']
#							except KeyError:
#								pass
							request.session.flush()
							request.session["user"] = userinfo
							client_ip = request.META.get('REMOTE_ADDR')
							print userinfo.user,client_ip
							loginlog = LoginLog(time=datetime.datetime.now(),user=userinfo.user,ip=client_ip)
							loginlog.save()
#							message=u"登入成功"
#							jsondata.update(message=message,statusCode="200",callbackType="closeCurrent")
						#							return HttpResponseRedirect("/index/")
							return HttpResponseRedirect("/index/")
						else:
							error = u"用户与密码不匹配"
							context.update({"error":error})
							return render_to_response("login.html",context,context_instance= RequestContext(request))
				else:
					error =u"未输入用户名!"
					context.update({"error":error})
					return render_to_response("login.html",context,context_instance= RequestContext(request))
			except Exception,e:
				traceback.print_exc()
#				message = e.message
		else:
			#转到登入窗口
			return render_to_response("login.html",{},context_instance= RequestContext(request))
	#		return render_to_response("signin.html",context,context_instance=RequestContext(request))
	except Exception,e:
		traceback.print_exc()
		raise Http404()


#def dialoglogin(request):
#	return render_to_response("dialogLogin.html",{},context_instance= RequestContext(request))

#def logout(request):
#	return render_to_response("login.html",{},context_instance= RequestContext(request))


def checkLogin(user):
	if user != None:
		return True
	else:
		return False

def requires_login(view):
	def new_view(request, *args, **kwargs):
		if hasattr(request, 'session'):
			user = request.session.get('user')
			if not checkLogin(user):
				if request.method =="POST":
					if request.is_ajax():
						jsondata = {"statusCode":"300","message":u"对不起,你可能是未登入,或者登入超时,没有权限访问此网页,您可以尝试重新登入!",}
						return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
					else:
						return render_to_response("notLogin.html")
				else:
					if request.is_ajax():
						jsondata = {"statusCode":"300","message":u"对不起,你可能是未登入,或者登入超时,没有权限访问此网页,您可以尝试重新登入!",}
						return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
					else:
						return render_to_response("notLogin.html")
					return render_to_response("notLogin.html")
			else:
				return view(request, *args, **kwargs)
		else:
			return Exception(u"您的网页不支持session")
	return new_view


def requires_root(view):
	def new_view(request, *args, **kwargs):
		user = request.session.get('user')
#		rootuser = User.objects.get(username="root")
		if user is not None and user.user =="root":
			return view(request, *args, **kwargs)
		else:
			 return response.responsenoPermission(request)
	return new_view
#def require_validate(view):
#	def __check_permisssion():
#		return view
#	return __check_permisssion
@requires_login
def require_validate(request,type,id):  #add wrapper to recevie decorator's parameter
	user = get_user_by_session(request.session)
	if user.has_permission(type,id):
		return True
	else:
		if request.method =="POST":
			if request.is_ajax():
				jsondata = {"statusCode":"300","message":u"对不起,您没有权限访问此网页!",}
				return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
			else:
				return render_to_response("noPermission.html")
		else:
			return render_to_response("noPermission.html")

#	def check_permission(func):
#		def __check_permission(request, *args, **kwargs):
#			user = request.session.get("user")
#			if user.has_permission(type,id):
#				func()
#			else:
#				return Http404();
#		return __check_permission
#	return check_permission    #return original decorator



'''
登入系统
'''
def dialoglogin(request):
	error = u""
	jsondata ={
		"navTabId":"",
		"rel":"",
		"callbackType":"",
		"forwardUrl":"",
		"confirmMsg":"",
		}
	try:
		if request.method == "POST":
			#验证用户名和密码
			try:
				username = request.POST.get("username")
				password = request.POST.get("password")
				if username:
					try:
						userinfo = User.objects.get(user = username)
					except User.DoesNotExist,e:
						message =u"用户不存在!"
						jsondata.update(message=message,statusCode="300")
					except User.MultipleObjectsReturned,e:
						message =u"用户错误!"
						jsondata.update(message=message,statusCode="300")
					else:
						if password == userinfo.passwd:
							request.session["user"] = userinfo
							message=u"登入成功"
							jsondata.update(message=message,statusCode="200",callbackType="closeCurrent")
#							return HttpResponseRedirect("/index/")
						else:
							message = u"密码不正确"
							jsondata.update(message=message,statusCode="300")
				else:
					message =u"未输入用户名!"
					jsondata.update(message=message,statusCode="300")
			except Exception,e:
				traceback.print_exc()
				message = e.message
				jsondata.update(message=message,statusCode="300")
			finally:
				return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
		else:
			#转到登入窗口
			return render_to_response("dialogLogin.html",{},context_instance= RequestContext(request))
#		return render_to_response("signin.html",context,context_instance=RequestContext(request))
	except Exception,e:
		traceback.print_exc()
		raise Http404()
'''
登出系统
'''

@csrf_exempt
def logout(request):
#	logger.info(u"logout")
	jsondata ={}
	try:
		pass
#		del request.session['user']
		#        return HttpResponse(u"你已安全退出")
#		return HttpResponseRedirect('/login/')
#		jsondata.update()
#		jsondata.update({"statusCode":"200","message":"您已安全退出"})
#		"callbackType":"forward","forwardUrl":"/login/"
	except KeyError:
		pass
#		jsondata.update({"statusCode":"200","message":"您已经处于登出状态,无需退出"})
	finally:
		request.session.flush()
		return HttpResponseRedirect('/login/')
#		return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
		#return HttpResponse(u"你尚未登录，无须退出")
#		return HttpResponseRedirect('/login/')

#密码修改
#判断用户原密码是否正确,正确保存新密码
@requires_login
def change_password(request):
	try:
		if request.method =="POST":
			jsondata ={
				"navTabId":"",
				"rel":"",
				"callbackType":"closeCurrent",
				"forwardUrl":"",
				"confirmMsg":"",
				}
			old_password = request.POST.get("old_password","")
			new_password = request.POST.get("new_password","")
			new_password2 = request.POST.get("new_password2","")
			if old_password and new_password and new_password2:
				if new_password == new_password2:
					session_user = request.session.get("user")
					try:
						user = User.objects.get(pk=session_user.id)
					except User.DoesNotExist,e:
						jsondata.update({"message":u"您可能已被管理员删除,请尝试重新登入","statusCode":"300"})
					else:
						if old_password == user.passwd:
							user.passwd = new_password
							user.save()
							jsondata.update({"message":u"密码修改成功,建议重新登入系统","statusCode":"200"})
						else:
							jsondata.update({"message":u"原密码不正确,密码修改失败","statusCode":"300"})
				else:
					jsondata.update({"message":u"两次密码不匹配,密码修改失败","statusCode":"300"})
			else:
				jsondata.update({"message":u"输入数据错误,密码修改失败","statusCode":"300"})
			return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
		else:
			return render_to_response("user/change_password.html",Context(),context_instance=RequestContext(request))
	except Exception,e:
		traceback.print_exc()
		raise Http404()


#根据session获取用户
def get_user_by_session(session):
	user = session.get("user","")
	return user



def get_belongs_org_by_user(user):
	return user.org

#根据session来获取所属机构,未登入用户返回none
def get_belong_org_by_session(session):
	user = get_user_by_session(session)
	if user:
		org = get_belongs_org_by_user(user)
		return org
	else:
		return None

#get_org_tree_json

@requires_login
@never_cache
def get_org_tree_json(request):
	'''
	根据当前用户所属的机构来确定构建机构树的根结点
	'''
	try:
		log.info("get_org_tree_json views begin...")
		#获取根机构结点
		user = get_user_by_session(request.session)
		belong_org = user.org
		parent_org = belong_org
		orgs_queryset = Organization.objects.filter(link__startswith=parent_org.link).order_by("id")
		orgs_tree_json = getJson(orgs_tree=orgs_queryset)
		response = HttpResponse(orgs_tree_json,mimetype = 'application/javascript')
#		response['Cache-Control'] = 'no-cache'

		return response
	#		return render_to_response("org/organization.html")
	except:
		traceback.print_exc()

#get_org_tree_json
@requires_login
@never_cache
def get_org_tree_json2(request):
	'''
	根据当前用户所属的机构来确定构建机构树的根结点
	'''
	try:
		#获取根机构结点
		user = request.session.get("user")
		belong_org = user.org
		parent_org = belong_org
		parent_tree_org = TreeNode.objects.get(type=1,obj_id=parent_org.id)
		orgs_tree = TreeNode.objects.filter(Q(type=1) | Q(type=3),link__startswith=parent_tree_org.link).order_by("type",'id')
		orgs_tree_json = getJson(orgs_tree=orgs_tree)

		return HttpResponse(orgs_tree_json,mimetype = 'application/javascript')
	#		return render_to_response("org/organization.html")
	except:
		traceback.print_exc()

def has_permission(request,id,type):
	pass