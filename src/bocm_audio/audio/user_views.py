__author__ = 'daitr'
#-*-coding:utf-8-*-

import traceback
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.template import Context,RequestContext
from django.db.utils import IntegrityError
from django.db import transaction

from audio.constants import STATUS_CODE
from utils.pageHandle import getPage

from audio.models import *
from audio.account import *
from utils.MyEncoder import getJson

import logging
log = logging.getLogger('audio_logger')

import xlwt
@requires_login
def user(request):
	'''
	根据当前用户所属的机构来确定构建机构树的根结点
	'''
	try:
		#获取根机构结点
#		orgs_tree = TreeNode.objects.filter(type=1,link__startswith="1_")
		context=({
#			'treenode_list':orgs_tree,
			})
		return render_to_response("user/user.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()
#
##get_org_tree_json
#def get_org_tree_json(request):
#	'''
#	根据当前用户所属的机构来确定构建机构树的根结点
#	'''
#	try:
#		#获取根机构结点
#		orgs_tree = TreeNode.objects.filter(type=1,link__contains="1_")
#		orgs_tree_json = getJson(orgs_tree=orgs_tree)
#		return HttpResponse(orgs_tree_json,mimetype = 'application/javascript')
#	#		return render_to_response("org/organization.html")
#	except:
#		traceback.print_exc()

@csrf_exempt
@requires_login
def user_list(request):
	#分页
	pageNum = 1
	numPerPage = 10
	#查询字段
	user_username=""
	user_user=""
	user_name=""
	user_addr=""
	root_org_id =-1
	try:
		if request.method == "POST":
			user_username = request.POST.get("user_username","")
			user_name = request.POST.get("user_name","")
			user_addr = request.POST.get("user_addr","")
			user_user = request.POST.get("user_user","")

			pageNumstr = request.POST.get("pageNum",1) #  当前页
			numPerPagestr = request.POST.get("numPerPage",10)
			tree_select_org_idstr = int(request.POST.get("tree_select_org_id",""))
			try:
				pageNum=int(pageNumstr)
				numPerPage = int(numPerPagestr)
				tree_select_org_id = int(tree_select_org_idstr)
				root_org_id = tree_select_org_id
			except ValueError,e:
				raise Http404()
		else:
			org_id = request.GET.get("org_id","")
			if org_id:
				root_org_id = int(org_id)
				tree_select_org_id = root_org_id
			#每页显示数量
		#		orderField = request.POST.get("orderField","")
		#		orderDirection = request.POST.get("orderDirection","")
		#		pageNum = request.POST.get("","")
		try:
			parent_org = Organization.objects.get(pk=root_org_id)
		except Organization.DoesNotExist,e1:
			return HttpResponse("机构不存在或者已经被删除!")
		else:
			children_org_queryset = Organization.objects.filter(link__startswith=parent_org.link)
			#print user_user,user_name,user_addr
			user_list = User.objects.filter(org__in=children_org_queryset,user__contains=user_user)
			onePageresults = getPage(user_list,numPerPage,pageNum)

			paginator = onePageresults.paginator
			result_user_list = onePageresults.object_list #要显示的记录

			totalCount = paginator.count #总数量
			numPerPage = paginator.per_page #每页显示的数量
			pageCount = paginator.num_pages
			currentPage = pageNum #当前页
			pageNumShown = 5  #显示页标个数

			context = Context({
				'obj_list':result_user_list,
				'totalCount':totalCount,
				'numPerPage':numPerPage,
				'currentPage':currentPage,
				'pageNumShown':pageNumShown,
				'pageCount': pageCount,
				'user_username':user_username,
				'user_name':user_name,
				'user_addr':user_addr,
				'user_user':user_user,
				"tree_select_org_id":tree_select_org_id,

				})
			return render_to_response("user/user_list.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()



@requires_login
def user_add(request):
	"""
	根据用户所属机构确定用户所拥有的子机构
	用户可以删除下属机构的用户
	"""
	jsondata ={
		"navTabId":"",
		"rel":"userBox",
		"callbackType":"closeCurrent",
	}
	try:
		if request.is_ajax():
			print "is_ajax:true"
		else:
			print "is_ajax:false"

		if request.method == 'POST':
			#暂时不支持更改所属机构
			parent_id = request.POST.get("org_parent.id","")
			parent_name = request.POST.get("org_parent.name","")
			username = request.POST.get("username","")
			password = request.POST.get("password","")
			name = request.POST.get("name","")
			phone = request.POST.get("phone","")
			address = request.POST.get("address","")
			email = request.POST.get("email","")
#			rights = request.POST.get("rights","")
			user_id  = request.POST.get("id")
			if user_id:
				user_set = User.objects.filter(user=username).exclude(pk=user_id)
			else:
				user_set = User.objects.filter(user=username)
			if user_set.count()>=1:
				jsondata.update({"statusCode":"300", "message":u"操作失败,已经存在同名的用户名,请换一个试试","callbackType":"closeCurrent"})
				return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
			if user_id:
				#修改已存在的机构,暂时不支持所属机构的修改
				#判断是否存在用户:
				try:
					user_id = int(user_id)
					user = User.objects.get(pk=user_id)
					olduser = user.user
					user.user = username
					user.passwd = password
					user.name = name
					user.phone = phone
					user.address= address
					user.email = email
					user.rights= 1
					user.save()
					UserLog.objects.log_action(request,UserLog.EDIT_OPT,UserLog.USER,olduser,user)
					user_treenode =TreeNode.objects.get(type=2,obj_id=user.id)
					user_treenode.name = username
					user_treenode.save()
					jsondata.update(STATUS_CODE["sucesss"],callbackType="closeCurrent")
					return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
				except ValueError:
					traceback.print_exc()
				except Exception:
					traceback.print_exc()
			else:
				#不存在的机构直接添加
				user = User(user=username,passwd=password,name=name,org_id=parent_id,phone=phone,address=address,email=email,rights=1)
				try:
					#找出树结点中新建机构的所属机构信息
					parentTreeNode = TreeNode.objects.get(type=1,obj_id=parent_id)
					user.save()
					UserLog.objects.log_action(request,UserLog.ADD_OPT,UserLog.USER,user)
					newTreeNode = TreeNode(parent_id=parentTreeNode.id,name=username,type=2,obj_id=user.id,level=parentTreeNode.level+1)
					newTreeNode.save()
					newTreeNode.link = parentTreeNode.link + str(newTreeNode.id)+"_"
					newTreeNode.save()
				except Exception:
					traceback.print_exc()
				else:
					#根据所属机构及提交信息构建树节点的机构信息
					jsondata.update(STATUS_CODE["sucesss"])
					return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
			#		return HttpResponse(simplejson.dumps({"statusCode":200, "navTabId":request.POST.get('navTabId','newsindex'), "callbackType":request.POST.get('callbackType','closeCurrent'), "message":u'添加成功'}), mimetype='application/json')
		else:
			context = Context({})
			user_id = request.GET.get("id","")
#			通过连接打开添加或者修改表单,GET请求方式
			opMethod = request.GET.get("opMethod","")
			context = Context({"opMethod":opMethod})
			if opMethod=="add":
				#			添加机构时候返回父机构
				parent_org_id =  request.GET.get("parent_org_id","")
				try:
					parent_org_id = int(parent_org_id)
				except ValueError:
					raise Exception(u"获取id值错误")
				else:
					parent_org = Organization.objects.get(pk=parent_org_id)
					#					parent_org={"id":parent_org_id.id,"name":parent_org_id.name}
					context = context.update({"parent_org":parent_org})
			elif opMethod=="edit":
				#当修改机构时候,获取机构信息,返回页面
				try:
					user_id = int(user_id)
				except ValueError:
					raise Exception(u"获取id值错误")
				else:
					user = User.objects.get(pk=user_id)
					context = context.update({"user":user,})
			else:
				pass
			#			return render_to_response("terminal/archive/playArchive.html",context,context_instance=RequestContext(request))
			context.update(opMethod=opMethod)
			return render_to_response("user/user_add.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()
		jsondata.update(STATUS_CODE["failure"])
		return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
#
#
#
#@csrf_exempt
#def get_org_objs(request):
#	try:
#		org_list =[]
#		org_queryset = Organization.objects.all()
#		for org in org_queryset:
#			org_dict={"id":org.id,"name":org.name}
#			org_list.append(org_dict)
#		#		jsondata = [
#		#				{"id":{"aa":{"cc":"dd"}}, "name":"技术部", "orgNum":"1001"},
#		#				{"id":"2", "name":"人事部", "orgNum":"1002"},
#		#				{"id":"3", "name":"销售部", "orgNum":"1003"},
#		#				{"id":"4", "name":"售后部", "orgNum":"1004"}
#		#		]
#		#	org_list = Organization.objects.all()
#		#	jsondata = getJson(orgs=org_list)
#		return HttpResponse(simplejson.dumps(org_list),mimetype = 'application/javascript')
#	except:
#		traceback.print_exc()
#
#@csrf_exempt
#def org_deletemany(request):
#	"""
#		批量删除记录
#	"""
#	try:
#		if request.method =="POST":
#			ids = request.POST.getlist("ids","")
#			orgs = Organization.objects.filter(id__in=ids)
#			for org in orgs:
#				print org
#		jsondata = {
#			"statusCode":"200",
#			"message":u"删除成功",
#			"navTabId":"",
#			"rel":"",
#			"callbackType":"",
#			"forwardUrl":"",
#			"confirmMsg":""
#		}
#		return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')
#	except:
#		traceback.print_exc()

@csrf_exempt
@requires_login
def user_delete(request):
	"""
		删除记录
	"""
	jsondata = {
		"rel":"userBox",
		}
	try:
		if request.method =="POST":
			id = request.GET.get("id","")
			if id:
				try:
					id = int(id)
				except Exception:
					traceback.print_exc()
				else:
					try:
						user_treenode = TreeNode.objects.get(type=2,obj_id=id)
						user = User.objects.get(pk=id)
						username = user.user
					except TreeNode.DoesNotExist,e1 :
						jsondata.update({
							"statusCode":"300",
							"message":u'删除失败,用户不存在,或已被删除!',
							})
						return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')
					else:
						try:
							user.delete()
							user_treenode.delete()
						except models.ProtectedError,e2:
							jsondata.update({
								"statusCode":"300",
								"message":u'删除失败,在删除此用户之前,您需要先删除用户下录音资料!',
								})
							return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')
						else:
							UserLog.objects.log_action(request,UserLog.DELE_OPT,UserLog.USER,username)
							jsondata.update({
								"statusCode":"200",
								"message":u"删除成功",
								})
						return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')

	except:
		traceback.print_exc()


@requires_login
def users_export(request):
	try:
		if request.method == "GET":
			UserLog.objects.log_action(request,UserLog.EXPORT_OPT,UserLog.USER)
			user_username = request.GET.get("user_username","")
			user_name = request.GET.get("user_name","")
			user_addr = request.GET.get("user_addr","")
			user_user = request.GET.get("user_user","")
			root_org_id = int(request.GET.get("tree_select_org_id",""))
			parent_org = Organization.objects.get(pk=root_org_id)
			children_org_queryset = Organization.objects.filter(link__startswith=parent_org.link)
			user_queryset = User.objects.filter(org__in=children_org_queryset,user__contains=user_user,name__contains=user_name,address__contains=user_addr)
#			now = datetime.now()
#			filename = now.strftime("%Y%m%d%H%M%S")+".xls"
			filename = u"用户信息.xls"
			filename = filename.encode("gbk")
			response = HttpResponse(mimetype="application/ms-excel")
			response['Content-Disposition'] = 'attachment; filename='+filename
			wb = xlwt.Workbook()
			ws = wb.add_sheet(u'用户信息')
			ws.write(0,0,u"用户名")
			ws.write(0,1,u"所属机构")
			ws.write(0,2,u"姓名")
			ws.write(0,3,u"电话")
			ws.write(0,4,u"地址")
			ws.write(0,5,u"邮件")
			row = 1
			for user in user_queryset:
				ws.write(row,0,user.user)
				ws.write(row,1,user.org.name)
				ws.write(row,2,user.name)
				ws.write(row,3,user.phone)
				ws.write(row,4,user.address)
				ws.write(row,5,user.email)
				row +=1
			wb.save(response)
			return response

	except Exception,e:
		traceback.print_exc()
