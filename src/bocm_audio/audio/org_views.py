__author__ = 'daitr'
#-*-coding:utf-8-*-

import traceback
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.template import Context,RequestContext
from django.db import models
import datetime
import xlwt

from audio.constants import STATUS_CODE
from utils.pageHandle import getPage
from audio.account import *
from audio.models import *
from utils.MyEncoder import getJson

import logging
from django.utils.encoding import force_unicode

log = logging.getLogger('audio_logger')

@requires_login
def organization(request):
	'''
	根据当前用户所属的机构来确定构建机构树的根结点
	'''
#	orgs = get_belong_org_by_session(request)
	log.info("organization views begin...")
	try:
		#获取根机构结点
#		orgs_tree = TreeNode.objects.filter(type=1,link__startswith="1_")
		context=({
#			'treenode_list':orgs_tree,
		})
		return render_to_response("org/organization.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()


@csrf_exempt
@requires_login
def org_list(request):
	pageNum = 1
	numPerPage = 10
	#查询字段
	org_name=""
	org_phone=""
	org_addr=""
	org_sid=""

	root_org_id =-1
	try:
		if request.method == "POST":
			org_name = request.POST.get("org_name","")
			org_phone = request.POST.get("org_phone","")
			org_addr = request.POST.get("org_addr","")
			org_sid = request.POST.get("org_sid","")

			pageNumstr = request.POST.get("pageNum",1) #  当前页
			numPerPagestr = request.POST.get("numPerPage",10)
			tree_select_org_idstr = int(request.POST.get("tree_select_org_id",""))
			try:
				pageNum=int(pageNumstr)
				numPerPage = int(numPerPagestr)
				tree_select_org_id = int(tree_select_org_idstr)
				root_org_id = tree_select_org_id
			except ValueError,e:
				pass
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
			org_list = Organization.objects.filter(link__startswith=parent_org.link,name__contains=org_name,phone__contains=org_phone,address__contains=org_addr,org_sid__contains=org_sid).order_by("id")
			onePageresults = getPage(org_list,numPerPage,pageNum)

			paginator = onePageresults.paginator
			result_org_list = onePageresults.object_list #要显示的记录

			totalCount = paginator.count #总数量
			numPerPage = paginator.per_page #每页显示的数量
			pageCount = paginator.num_pages
			currentPage = pageNum #当前页
			pageNumShown = 5  #显示页标个数

			context = Context({
				'obj_list':result_org_list,
				'totalCount':totalCount,
				'numPerPage':numPerPage,
				'currentPage':currentPage,
				'pageNumShown':pageNumShown,
				'pageCount': pageCount,
				'org_name':org_name,
				'org_phone':org_phone,
				'org_addr':org_addr,
				'org_sid':org_sid,
				"tree_select_org_id":tree_select_org_id,

			})
			return render_to_response("org/org_list.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()


@requires_login
def org_add(request):
	"""
	"""
	jsondata ={
#		"navTabId":"organization",
		"rel":"orgBox",
		"callbackType":"closeCurrent",
		"forwardUrl":"",
		"confirmMsg":"",
	}
	try:
#		if request.is_ajax():
#			print "is_ajax:true"
#		else:
#			print "is_ajax:false"
		user = request.session.get("user")

		if request.method == 'POST':
			#暂时不支持更改父机构
			parent_id = request.POST.get("org_parent.id","")
			parent_name = request.POST.get("org_parent.name","")
			name = request.POST.get("name","")
			org_sid = request.POST.get("org_sid","")
			phone = request.POST.get("phone","")
			address = request.POST.get("address","")
			memo = request.POST.get("memo","")
			org_id  = request.POST.get("id")
			if org_id:
				#修改已存在的机构,暂时不支持所属机构的修改
				try:
					org_id = int(org_id)
					org = Organization.objects.get(pk=org_id)
					old_org = org.name
					org.name = name
					org.org_sid = org_sid
					org.phone = phone
					org.memo= memo
					org.save()
					UserLog.objects.log_action(request,UserLog.EDIT_OPT,UserLog.ORG,old_org,org)
					org_treenode =TreeNode.objects.get(type=1,obj_id=org.id)
					org_treenode.name = name
					org_treenode.save()
					jsondata.update(STATUS_CODE["sucesss"],callbackType="closeCurrent",orgName=org.name,orgId=str(org.id),opMethod="edit")
					return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
				except ValueError:
					traceback.print_exc()
				except Exception:
					traceback.print_exc()
			else:
				#不存在的机构直接添加
				org = Organization(name=name,parent_id=parent_id,phone=phone,address=address,memo=memo,org_sid=org_sid)
				org.save()
				org.link = org.parent.link + str(org.id)+"_"
				org.save()
				try:
					#找出树结点中新建机构的所属机构信息
					parentTreeNode = TreeNode.objects.get(type=1,obj_id=parent_id)
				except Exception:
					traceback.print_exc()
				else:
					#根据所属机构及提交信息构建树节点的机构信息
					newTreeNode = TreeNode(parent_id=parentTreeNode.id,name=name,type=1,obj_id=org.id,level=parentTreeNode.level+1)
					newTreeNode.save()
					newTreeNode.link = parentTreeNode.link + str(newTreeNode.id)+"_"
					newTreeNode.save()
					UserLog.objects.log_action(request,UserLog.ADD_OPT,UserLog.ORG,org)
					jsondata.update(STATUS_CODE["sucesss"],orgName=org.name,orgId=str(org.id),opMethod="add",parent_id=parent_id)
				return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
				#		return HttpResponse(simplejson.dumps({"statusCode":200, "navTabId":request.POST.get('navTabId','newsindex'), "callbackType":request.POST.get('callbackType','closeCurrent'), "message":u'添加成功'}), mimetype='application/json')
		else:
#			通过连接打开添加或者修改表单,GET请求方式
			opMethod = request.GET.get("opMethod")
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
				org_id = request.GET.get("id","")
				try:
					org_id = int(org_id)
				except ValueError:
					raise Exception(u"获取id值错误")
				else:
					org = Organization.objects.get(pk=org_id)
					context = context.update({"org":org,})
			else:
				pass
#			return render_to_response("terminal/archive/playArchive.html",context,context_instance=RequestContext(request))
			context.update(opMethod=opMethod)
			return render_to_response("org/org_add.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()
		jsondata.update(STATUS_CODE["failure"])
		return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')



@csrf_exempt
@requires_login
def get_org_objs(request):
	try:
		org_list =[]
		org_queryset = Organization.objects.all()
		for org in org_queryset:
			org_dict={"id":org.id,"name":org.name}
			org_list.append(org_dict)
#		jsondata = [
#				{"id":{"aa":{"cc":"dd"}}, "name":"技术部", "orgNum":"1001"},
#				{"id":"2", "name":"人事部", "orgNum":"1002"},
#				{"id":"3", "name":"销售部", "orgNum":"1003"},
#				{"id":"4", "name":"售后部", "orgNum":"1004"}
#		]
		#	org_list = Organization.objects.all()
		#	jsondata = getJson(orgs=org_list)
		return HttpResponse(simplejson.dumps(org_list),mimetype = 'application/javascript')
	except:
		traceback.print_exc()

@csrf_exempt
@requires_login
def org_deletemany(request):
	"""
		批量删除记录
	"""
	try:
		if request.method =="POST":
			ids = request.POST.getlist("ids","")
			orgs = Organization.objects.filter(id__in=ids)
			for org in orgs:
				print org
		jsondata = {
			"statusCode":"200",
			"message":u"删除成功",
			"navTabId":"",
			"rel":"",
		}
		return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')
	except:
		traceback.print_exc()

@csrf_exempt
@requires_login
def org_delete(request):
	"""
		删除记录
	"""
	try:
		if request.method =="POST":
			id = request.GET.get("id","")
			if id:
				try:
					id = int(id)
				except Exception:
					traceback.print_exc()
				else:
					org_treenode = TreeNode.objects.get(type=1,obj_id=id)
					child_orgs = TreeNode.objects.filter(parent__id=org_treenode.id)
					if child_orgs.count():
						messsage= u'机构不能被删除,'
						jsondata = {
							"statusCode":"300",
							"message":u'删除失败,机构不能被删除,必须先删除机构下的子机构,用户及设备',
							"rel":"orgBox",
						}
					else:
						org_treenode.delete()
						org = Organization.objects.get(pk=id)
						orgname= org.name
						org.delete()
						UserLog.objects.log_action(request,UserLog.DELE_OPT,UserLog.ORG,orgname)
						jsondata = {
							"statusCode":"200",
							"message":u"删除成功",
							"rel":"orgBox",
							"org_id":str(id),
						}
					return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')

	except:
		traceback.print_exc()



@requires_login
def orgs_export(request):
	try:
		if request.method == "GET":
			UserLog.objects.log_action(request,UserLog.EXPORT_OPT,UserLog.ORG)
			org_name = request.GET.get("org_name","")
			org_phone = request.GET.get("org_phone","")
			org_addr = request.GET.get("org_addr","")
			org_sid = request.GET.get("org_sid","")

			root_org_id = int(request.GET.get("tree_select_org_id",""))
			parent_org = Organization.objects.get(pk=root_org_id)

			org_queryset = Organization.objects.filter(link__startswith=parent_org.link,name__contains=org_name,phone__contains=org_phone,address__contains=org_addr,org_sid__contains=org_sid).order_by("id")
			now = datetime.datetime.now()
#			filename = now.strftime("%Y%m%d%H%M%S")+".xls"
			filename = u"机构信息.xls"
			filename = filename.encode("gbk")
			response = HttpResponse(mimetype="application/ms-excel")
			response['Content-Disposition'] = 'attachment; filename='+filename
			wb = xlwt.Workbook()
			ws = wb.add_sheet(u'机构信息')
			ws.write(0,0,u"名称")
			ws.write(0,1,u"机构编号")
			ws.write(0,2,u"直属机构")
			ws.write(0,3,u"电话")
			ws.write(0,4,u"地址")
			ws.write(0,5,u"说明")
			row = 1
			for org in org_queryset:
				ws.write(row,0,org.name)
				ws.write(row,1,org.org_sid)
				if org.parent:
					ws.write(row,2,org.parent.name)
				else:
					ws.write(row,2,"")
				ws.write(row,3,org.phone)
				ws.write(row,4,org.address)
				ws.write(row,5,org.memo)
				row +=1
			wb.save(response)
			return response

	except Exception,e:
		traceback.print_exc()




