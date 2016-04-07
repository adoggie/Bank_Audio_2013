__author__ = 'daitr'
#-*-coding:utf-8-*-

import traceback
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.template import Context,RequestContext

from audio.constants import STATUS_CODE
from audio.account import  *
from utils.pageHandle import getPage
from audio.models import *
from utils.MyEncoder import getJson
import xlwt


import logging
log = logging.getLogger('audio_logger')


@csrf_exempt
@requires_login
def terminal(request):
	'''
	根据当前用户所属的机构来确定构建机构树的根结点
	'''
	try:
		#获取根机构结点
		terminals_tree = TreeNode.objects.filter(type=1,link__startswith="1_")
		context=({
			'treenode_list':terminals_tree,
		})
		return render_to_response("terminal/terminal.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()

@csrf_exempt
@requires_login
def get_belong_terminal2(request):
	'''
	根据当前用户所属的机构来确定构建机构树的根结点
	'''
	try:
		#获取根机构结点
		user = request.session.get("user")
		org_tree_node = TreeNode.objects.get(obj_id=user.org.id,type=1)
		child_terminals_tree_node = TreeNode.objects.filter(link__startswith =org_tree_node.link,type=3)
		child_terminal_list =[]
		for child_terminal in child_terminals_tree_node:
			child_terminal={"id":child_terminal.obj_id,"name":child_terminal.name}
			child_terminal_list.append(child_terminal)
		return HttpResponse(simplejson.dumps(child_terminal_list),mimetype = 'application/javascript')
	except:
		traceback.print_exc()

@csrf_exempt
@requires_login
def terminal_list(request):
	pageNum = 1
	numPerPage = 10
	terminal_user=""   #话机编号
	terminal_employee=""   #员工名称
	terminal_addr=""     #地址
	try:
		if request.method == "POST":
			terminal_user = request.POST.get("terminal_user","")
			terminal_employee = request.POST.get("terminal_employee","")
			terminal_addr = request.POST.get("terminal_addr","")

			pageNumstr = request.POST.get("pageNum",1) #  当前页
			numPerPagestr = request.POST.get("numPerPage",10)
			tree_select_org_idstr = request.POST.get("tree_select_org_id","")
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
			#print children_org_queryset.count()
			terminal_list = Terminal.objects.filter(org__in=children_org_queryset,user__contains=terminal_user,employee__contains=terminal_employee,address__contains=terminal_addr)



			onePageresults = getPage(terminal_list,numPerPage,pageNum)

			paginator = onePageresults.paginator
			result_terminal_list = onePageresults.object_list #要显示的记录

			totalCount = paginator.count #总数量
			numPerPage = paginator.per_page #每页显示的数量
			pageCount = paginator.num_pages
			currentPage = pageNum #当前页
			pageNumShown = 5  #显示页标个数

			context = Context({
				'obj_list':result_terminal_list,
				'totalCount':totalCount,
				'numPerPage':numPerPage,
				'currentPage':currentPage,
				'pageNumShown':pageNumShown,
				'pageCount': pageCount,
				'terminal_user':terminal_user,
				'terminal_employee':terminal_employee,
				'terminal_addr':terminal_addr,
				"tree_select_org_id":tree_select_org_id,

			})
			return render_to_response("terminal/terminal_list.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()

#
#
@requires_login
def terminal_add(request):
	"""
	"""
	jsondata ={
		"navTabId":"",
		"rel":"terminalBox",
		"callbackType":"closeCurrent",
		"forwardUrl":"",
		"confirmMsg":""
	}
	try:
		userinfo = request.session.get("user")
		if request.is_ajax():
			print "is_ajax:true"
		else:
			print "is_ajax:false"

		if request.method == 'POST':
			#暂时不支持更改父机构
			parent_id = request.POST.get("terminal_parent.id","")
			parent_name = request.POST.get("terminal_parent.name","")
			user = request.POST.get("user","")
			passwd = request.POST.get("passwd","")
			address = request.POST.get("address","")
#			name = request.POST.get("name","")
			phone = request.POST.get("phone","")
			postcode = request.POST.get("postcode","")
			employee = request.POST.get("employee","")
			addition = request.POST.get("addition","")
			terminal_id  = request.POST.get("id")
			if terminal_id:
				term_set = User.objects.filter(user=user).exclude(pk=terminal_id)
			else:
				term_set = Terminal.objects.filter(user=user)

			if term_set.count()>=1:
				jsondata.update({"statusCode":"300", "message":u"操作失败,已有同名话机,请换一个名称试试","callbackType":"closeCurrent"})
				return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
			if terminal_id:
				#修改已存在的机构,暂时不支持所属机构的修改
				try:
					terminal_id = int(terminal_id)
					terminal = Terminal.objects.get(pk=terminal_id)
					oldterminal= terminal.user
					terminal.user =user
					terminal.passwd = passwd
					terminal.address = address
#					terminal.name = name
					terminal.phone = phone
					terminal.postcode = postcode
					terminal.employee = employee
					terminal.addition = addition
					terminal.save()
					UserLog.objects.log_action(request,UserLog.EDIT_OPT,UserLog.TERM,oldterminal,terminal)
					terminal_treenode =TreeNode.objects.get(type=3,obj_id=terminal.id)
#					terminal_treenode.name = name
					terminal_treenode.save()
					jsondata.update(STATUS_CODE["sucesss"])
					return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
				except ValueError:
					traceback.print_exc()
				except Exception:
					traceback.print_exc()
			else:
				#不存在的机构直接添加
				import datetime
				now = datetime.datetime.now()
				creator_id = userinfo.id                #创建者
				createtime = now   #创建时间
#				status = models.IntegerField(default=0)             #状态 0 - 未上线 ； 1 -在线
#				regtime = models.DateTimeField(null=True)                    #最近一次登录时间
				terminal = Terminal(user=user,passwd=passwd,org_id=parent_id,
				phone=phone,address=address,postcode=postcode,employee=employee,creator_id=creator_id,createtime=createtime,status=0,regtime=now)
				terminal.save()
				UserLog.objects.log_action(request,UserLog.ADD_OPT,UserLog.TERM,terminal)
				try:
					#找出树结点中新建机构的所属机构信息
					parentTreeNode = TreeNode.objects.get(type=1,obj_id=parent_id)
				except Exception:
					traceback.print_exc()
				else:
					#根据所属机构及提交信息构建树节点的机构信息
					newTreeNode = TreeNode(parent_id=parentTreeNode.id,name=user,type=3,obj_id=terminal.id,level=parentTreeNode.level+1)
					newTreeNode.save()
					newTreeNode.link = parentTreeNode.link + str(newTreeNode.id)+"_"
					newTreeNode.save()
					jsondata.update(STATUS_CODE["sucesss"])
				return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
				#		return HttpResponse(simplejson.dumps({"statusCode":200, "navTabId":request.POST.get('navTabId','newsindex'), "callbackType":request.POST.get('callbackType','closeCurrent'), "message":u'添加成功'}), mimetype='application/json')
		else:
			terminal_id = request.GET.get("id","")
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
					terminal_id = int(terminal_id)
				except ValueError:
					raise Exception(u"获取id值错误")
				else:
					terminal = Terminal.objects.get(pk=terminal_id)
					context = context.update({"terminal":terminal,})
			else:
				pass
			context.update(opMethod=opMethod)
			return render_to_response("terminal/terminal_add.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()
		jsondata.update(STATUS_CODE["failure"])
		return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')


#
#@csrf_exempt
#def get_org_objs(request):
#	try:
#		org_list =[]
#		org_queryset = Organization.objects.all()
#		for org in org_queryset:
#			org_dict={"id":org.id,"name":org.name}
#			org_list.append(org_dict)
##		jsondata = [
##				{"id":{"aa":{"cc":"dd"}}, "name":"技术部", "orgNum":"1001"},
##				{"id":"2", "name":"人事部", "orgNum":"1002"},
##				{"id":"3", "name":"销售部", "orgNum":"1003"},
##				{"id":"4", "name":"售后部", "orgNum":"1004"}
##		]
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
#
@csrf_exempt
@requires_login
def terminal_delete(request):
	"""
		删除设备
		要先删掉其下的录音资料和用户
	"""
	jsondata = {
		"rel":"terminalBox",
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
						terminal_treenode = TreeNode.objects.get(type=3,obj_id=id)
						terminal = Terminal.objects.get(pk=id)
						terminal_name = terminal.user
					except TreeNode.DoesNotExist,e1 :
						jsondata.update({
							"statusCode":"300",
							"message":u'删除失败,终端不存在,或已被删除!',
						})
						return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')
					else:
						try:
							terminal.delete()
							terminal_treenode.delete()
						except models.ProtectedError,e2:
							jsondata.update({
								"statusCode":"300",
								"message":u'删除失败,在删除此终端之前,您需要先删除终端下的客户信息和录音资料!',
								})
							return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')
						else:
							UserLog.objects.log_action(request,UserLog.DELE_OPT,UserLog.TERM,terminal_name)
							jsondata.update({
								"statusCode":"200",
								"message":u"删除成功",
							})
						return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')
	except:
		jsondata.update({
			"statusCode":"300",
			"message":u'删除失败,未知原因!',
			})
		traceback.print_exc()
		return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')

@requires_login
def terminals_export(request):
	try:
		if request.method == "GET":
			UserLog.objects.log_action(request,UserLog.EXPORT_OPT,UserLog.TERM)
			terminal_user = request.GET.get("terminal_user","")
			terminal_employee = request.GET.get("terminal_employee","")
			terminal_addr = request.GET.get("terminal_addr","")

			root_org_id = int(request.GET.get("tree_select_org_id"))
			parent_org = Organization.objects.get(pk=root_org_id)
			children_org_queryset = Organization.objects.filter(link__startswith=parent_org.link)
			terminal_queryset = Terminal.objects.filter(org__in=children_org_queryset,user__contains=terminal_user,employee__contains=terminal_employee,address__contains=terminal_addr)
#			now = datetime.now()
#			filename = now.strftime("%Y%m%d%H%M%S")+".xls"
			filename = u"终端信息.xls"
			filename = filename.encode("gbk")
			response = HttpResponse(mimetype="application/ms-excel")
			response['Content-Disposition'] = 'attachment; filename='+filename
			wb = xlwt.Workbook()
			ws = wb.add_sheet(u'终端信息')
			ws.write(0,0,u"话机编号")
			ws.write(0,1,u"所属机构")
			ws.write(0,2,u"地址")
			ws.write(0,3,u"电话")
			ws.write(0,4,u"邮编")
			ws.write(0,5,u"员工名称")
			ws.write(0,6,u"附属信息")
			ws.write(0,7,u"创建者")
			row = 1
			for terminal in terminal_queryset:
				ws.write(row,0,terminal.user)
				ws.write(row,1,terminal.org.name)
				ws.write(row,2,terminal.address)
				ws.write(row,3,terminal.phone)
				ws.write(row,4,terminal.postcode)
				ws.write(row,5,terminal.employee)
				ws.write(row,6,terminal.addition)
				ws.write(row,7,terminal.creator.name)
				row +=1
			wb.save(response)
			return response

	except Exception,e:
		traceback.print_exc()
