__author__ = 'daitr'
#-*-coding:utf-8-*-

import traceback
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.template import Context,RequestContext
from django.db.models import Q

from audio.constants import STATUS_CODE
from utils.pageHandle import getPage
from audio.account import *
from audio.models import *
from utils.MyEncoder import getJson
import xlwt

import logging
log = logging.getLogger('audio_logger')


@requires_login
def client(request):
	'''
	根据当前用户所属的机构来确定构建机构树的根结点
	'''
	try:
		#获取根机构结点
		orgs_tree = TreeNode.objects.filter(type=1,link__startswith="1_")
		context=({
			'treenode_list':orgs_tree,
		})
		return render_to_response("terminal/client/client.html",context,context_instance=RequestContext(request))
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
##		return render_to_response("org/organization.html")
#	except:
#		traceback.print_exc()
@csrf_exempt
@requires_login
def client_list(request):
	pageNum = 1
	numPerPage = 10
	client_name="" #客户名称
	client_sid="" #客户编号
	client_corp="" #客户公司
	client_clientid ="" #客户ID号,非表的id
	client_phone="" # 电话号码,包括phone1,phone2,phone3
	client_pinyin="" # 拼音码
	type="" #结点类型,是机构还是终端
	obj_id="" # 目标结点id
	try:
		if request.method == "POST":
			type = request.POST.get("type","").strip()
			obj_id = request.POST.get("obj_id","").strip()
			if type=="1":
				org_id = obj_id
				org = Organization.objects.get(id=org_id)
				children_org_set = Organization.objects.filter(link__startswith=org.link)
				term_set = Terminal.objects.filter(org__in=children_org_set)
			elif type=="3":
				terminal_id = obj_id
				term_set = Terminal.objects.filter(id=terminal_id)
			else:
				return Http404()
			client_name = request.POST.get("client_name","")
			client_sid = request.POST.get("client_sid","")
			client_corp = request.POST.get("client_corp","")
			client_clientid = request.POST.get("client_clientid","")
			client_phone = request.POST.get("client_phone","")
			client_pinyin = request.POST.get("client_pinyin","")
			pageNumstr = request.POST.get("pageNum",1) #  当前页
			numPerPagestr = request.POST.get("numPerPage",10)
			try:
				pageNum=int(pageNumstr)
				numPerPage = int(numPerPagestr)
			except ValueError,e:
				pass
		else:
			type = request.GET.get("type","").strip()
			obj_id = request.GET.get("obj_id","").strip()
			if type=="1":
#				org_id = obj_id
#				org = Organization.objects.get(id=org_id)
#				children_org_set = Organization.objects.filter(link__startswith=org.link)
#				term_set = Terminal.objects.filter(org__in=children_org_set)
				term_set= []
			elif type=="3":
				terminal_id = obj_id
				term_set = Terminal.objects.filter(id=terminal_id)
			else:
				return Http404()
		client_list = Client.objects.filter(Q(name__contains=client_name) | Q(pinyin__contains=client_name),
		Q(phone1__contains=client_phone) | Q(phone2__contains=client_phone)|Q(phone3__contains=client_phone),
		term__in=term_set,
		clientid__contains=client_clientid,sid__contains=client_sid,corp__contains=client_corp)

		onePageresults = getPage(client_list,numPerPage,pageNum)

		paginator = onePageresults.paginator
		result_client_list = onePageresults.object_list #要显示的记录

		totalCount = paginator.count #总数量
		numPerPage = paginator.per_page #每页显示的数量
		pageCount = paginator.num_pages
		currentPage = pageNum #当前页
		pageNumShown = 5  #显示页标个数

		context = Context({
			'obj_list':result_client_list,
			'totalCount':totalCount,
			'numPerPage':numPerPage,
			'currentPage':currentPage,
			'pageNumShown':pageNumShown,
			'pageCount': pageCount,
			'client_name':client_name,
			'client_sid':client_sid,
			'client_corp':client_corp,
			"client_clientid": client_clientid,
			"client_phone":client_phone,
			"client_pinyin":client_pinyin,
			'type':type,
			"obj_id":obj_id,

			})
		return render_to_response("terminal/client/client_list.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()
		raise Http404()


@requires_login
def client_add(request):
	"""
	"""
	jsondata ={
		"navTabId":"",
		"rel":"clientBox",
		"callbackType":"closeCurrent",
		"forwardUrl":"",
		"confirmMsg":""
	}
	try:
		if request.is_ajax():
			print "is_ajax:true"
		else:
			print "is_ajax:false"

		if request.method == 'POST':
			#暂时不支持更改父机构
			client_term_id = request.POST.get("client_term.id","")
			client_term_name = request.POST.get("client_term.name","")
			sid = request.POST.get("sid","")
			name = request.POST.get("name","")
			sex = request.POST.get("sex","")
			corp = request.POST.get("corp","")
			phone1   = request.POST.get("phone1","")
			phone2 = request.POST.get("phone2","")
			address = request.POST.get("address","")
			postcode = request.POST.get("postcode","")
			email = request.POST.get("email","")
			website = request.POST.get("website","")
			im = request.POST.get("im","")
			memo = request.POST.get("memo","")
			personid = request.POST.get("personid","")
			clientid = request.POST.get("clientid","")
			client_id  = request.POST.get("id")

			if client_id:
				#修改已存在的机构,暂时不支持所属机构的修改
				try:
					client_id = int(client_id)
					client = Client.objects.get(pk=client_id)
					client.sid = sid
					client.name = name
					client.sex = sex
					client.corp = corp
					client.phone1 = phone1
					client.phone2 = phone2
					client.address = address
					client.postcode = postcode
					client.email =email
					client.website =website
					client.im = im
					client.memo = memo
					client.personid = personid
					client.clientid = clientid
#					client.client_id = client_id
					client.save()
					jsondata.update(STATUS_CODE["sucesss"])
					return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
				except ValueError:
					traceback.print_exc()
				except Exception:
					traceback.print_exc()
			else:
				#不存在的机构直接添加
				client = Client(term_id=client_term_id,sid=sid,name=name,sex=sex,corp=corp,phone1=phone1,phone2=phone2,address=address,
				postcode=postcode,email=email,website=website,im=im,memo=memo,personid=personid,clientid=clientid)
				client.save()
#				try:
#					#找出树结点中新建机构的所属机构信息
#					client_termTreeNode = TreeNode.objects.get(type=1,obj_id=client_term_id)
#				except Exception:
#					traceback.print_exc()
#				else:
#					#根据所属机构及提交信息构建树节点的机构信息
#					newTreeNode = TreeNode(client_term_id=client_termTreeNode.id,name=name,type=1,obj_id=client.id,level=client_termTreeNode.level+1)
#					newTreeNode.save()
#					newTreeNode.link = client_termTreeNode.link + str(newTreeNode.id)+"_"
#					newTreeNode.save()
				jsondata.update(STATUS_CODE["sucesss"])
				return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
				#		return HttpResponse(simplejson.dumps({"statusCode":200, "navTabId":request.POST.get('navTabId','newsindex'), "callbackType":request.POST.get('callbackType','closeCurrent'), "message":u'添加成功'}), mimetype='application/json')
		else:
			client_id = request.GET.get("id","")
			context = Context({})
			if client_id:
			#当修改机构时候,获取机构信息,返回页面
				try:
					client_id = int(client_id)
				except ValueError:
					raise Exception(u"获取id值错误")
				else:
					client = Client.objects.get(pk=client_id)
					context = context.update({"client":client,})
			return render_to_response("terminal/client/client_add.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()
		jsondata.update(STATUS_CODE["failure"])
		return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')

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
def client_delete(request):
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
					client = Client.objects.get(pk=id)
					client.delete()
					jsondata = {
						"statusCode":"200",
						"message":u"删除成功",
						"rel":"clientBox",
					}
				return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')

	except:
		traceback.print_exc()
		jsondata = {
			"statusCode":"300",
			"message":u"删除失败",
			"rel":"clientBox",
			}
		return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')

@requires_login
def clients_export(request):
	try:
		if request.method == "GET":
			UserLog.objects.log_action(request,UserLog.EXPORT_OPT,UserLog.CLIENT)
			type = request.GET.get("type","").strip()
			obj_id = request.GET.get("obj_id","").strip()
			client_name = request.GET.get("client_name","")
			client_sid = request.GET.get("client_sid","")
			client_corp = request.GET.get("client_corp","")
			client_clientid = request.GET.get("client_clientid","")
			client_phone = request.GET.get("client_phone","")
			if type=="1":
				org_id = obj_id
				org = Organization.objects.get(id=org_id)
				children_org_set = Organization.objects.filter(link__startswith=org.link)
				term_set = Terminal.objects.filter(org__in=children_org_set)
				term_set= []
			elif type=="3":
				terminal_id = obj_id
				term_set = Terminal.objects.filter(id=terminal_id)
			else:
				return Http404()
			client_list = Client.objects.filter(Q(name__contains=client_name) | Q(pinyin__contains=client_name),
				Q(phone1__contains=client_phone) | Q(phone2__contains=client_phone)|Q(phone3__contains=client_phone),
				term__in=term_set,
				clientid__contains=client_clientid,sid__contains=client_sid,corp__contains=client_corp)

#			now = datetime.now()
#			filename = now.strftime("%Y%m%d%H%M%S")+".xls"
			filename = u"客户信息.xls"
			filename = filename.encode("gbk")
			response = HttpResponse(mimetype="application/ms-excel")
			response['Content-Disposition'] = 'attachment; filename='+filename
			wb = xlwt.Workbook()
			ws = wb.add_sheet(u'客户信息')
			ws.write(0,0,u"客户名称")
			ws.write(0,1,u"所属终端")
			ws.write(0,2,u"性别")
			ws.write(0,3,u"公司")
			ws.write(0,4,u"电话1")
			ws.write(0,5,u"电话2")
			ws.write(0,6,u"电话3")
			ws.write(0,7,u"地址")
			ws.write(0,8,u"邮编")
			ws.write(0,9,u"邮箱")
			ws.write(0,10,u"网址")
			ws.write(0,11,u"IM")
			ws.write(0,12,u"身份证号")
			ws.write(0,13,u"客户归属")
			ws.write(0,14,u"客户类型")

			row = 1
			for client in client_list:
				ws.write(row,0,client.name)
				ws.write(row,1,client.term.user)
				ws.write(row,2,client.get_sex_display())
				ws.write(row,3,client.corp)
				ws.write(row,4,client.phone1)
				ws.write(row,5,client.phone2)
				ws.write(row,6,client.phone3)
				ws.write(row,7,client.address)
				ws.write(row,8,client.postcode)
				ws.write(row,9,client.email)
				ws.write(row,10,client.website)
				ws.write(row,11,client.im)
				ws.write(row,12,client.personid)
				ws.write(row,13,client.owner_org)
				ws.write(row,14,client.get_type_display())
				row +=1
			wb.save(response)
			return response

	except Exception,e:
		traceback.print_exc()