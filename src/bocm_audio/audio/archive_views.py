__author__ = 'daitr'
#-*-coding:utf-8-*-

import traceback,shutil
import datetime
import os
import xlwt

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.template import Context,RequestContext
from django.db.models import Q
from django.db.models import Count,Sum
from django.conf import settings

from audio.constants import STATUS_CODE
from utils.pageHandle import getPage
from audio.account import *
from audio.models import *
from utils.MyEncoder import getJson
from utils.formatTime import formatTimeLength
from utils.filesize import  intB2ReadableStr
import logging
log = logging.getLogger('audio_logger')
@requires_login
def archive(request):
	'''
	根据当前用户所属的机构来确定构建机构树的根结点
	'''
	try:
		#获取根机构结点
		orgs_tree = TreeNode.objects.filter(type=1,link__startswith="1_")
		context=({
			'treenode_list':orgs_tree,
		})
		return render_to_response("terminal/archive/archive.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()

##get_org_tree_json
#def get_org_tree_json(request):
#	'''
#	根据当前用户所属的机构来确定构建机构树的根结点
#	'''
#	try:
#		#获取根机构结点
#		orgs_tree = TreeNode.objects.filter(type=1,link__icontains="1_")
#		orgs_tree_json = getJson(orgs_tree=orgs_tree)
#		return HttpResponse(orgs_tree_json,mimetype = 'application/javascript')
##		return render_to_response("org/organization.html")
#	except:
#		traceback.print_exc()
#@csrf_exempt
@requires_login
def archive_list(request):
	pageNum = 1
	numPerPage = 10
	archive_name=""
#	archive_phone=""
#	archive_addr=""
	begin_time=""
	end_time=""
	archive_attr="-1"
	archive_type="-1"
	client_name=""
	archive_memo=""
	client_clientid=""
	archive_operator=""
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
			archive_name = request.POST.get("archive_name","")
#			archive_phone = request.POST.get("archive_phone","")
#			archive_addr = request.POST.get("archive_addr","")
			begin_time = request.POST.get("begin_time","")
			end_time = request.POST.get("end_time","")
			archive_attr = request.POST.get("archive_attr","-1")
			archive_type = request.POST.get("archive_type","-1")
			client_name = request.POST.get("client_name","")
			archive_memo = request.POST.get("archive_memo","")
			client_clientid = request.POST.get("client_clientid","")
			archive_operator = request.POST.get("archive_operator","")

			pageNumstr = request.POST.get("pageNum",1) #  当前页
			numPerPagestr = request.POST.get("numPerPage",10)
			try:
				pageNum=int(pageNumstr)
				numPerPage = int(numPerPagestr)
			except ValueError,e:
				traceback.print_exc()
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
#			date_end_time = datetime.datetime.now()
#			date_begin_time = date_end_time - datetime.timedelta(days=30)
			date_begin = datetime.date.today()
			date_end = date_begin + datetime.timedelta(days=1)

			begin_time = date_begin.strftime("%Y-%m-%d %H:%M:%S")
			end_time = date_end.strftime("%Y-%m-%d %H:%M:%S")
		archive_queryset = Archive.objects.filter(term__in=term_set)
		if client_name:
			archive_queryset = archive_queryset.filter(Q(client__name__icontains=client_name) | Q(client__pinyin__icontains=client_name),
			)
		if client_clientid:
			archive_queryset = archive_queryset.filter(client__clientid__icontains=client_clientid)
		archive_queryset = archive_queryset.filter(memo__icontains=archive_memo)
		if archive_attr and archive_attr!="-1":
			archive_queryset = archive_queryset.filter(attr=archive_attr)
#				print archive_type
		if archive_type and archive_type!="-1":
			archive_queryset = archive_queryset.filter(type=archive_type)
		if begin_time:
			archive_queryset = archive_queryset.filter(rectime__gte=begin_time)
		if end_time:
			archive_queryset = archive_queryset.filter(rectime__lte=end_time)
		if archive_operator:
			archive_queryset = archive_queryset.filter(operator__contains=archive_operator)
		onePageresults = getPage(archive_queryset,numPerPage,pageNum)

		paginator = onePageresults.paginator
		result_archive_list = onePageresults.object_list #要显示的记录

		totalCount = paginator.count #总数量
		numPerPage = paginator.per_page #每页显示的数量
		pageCount = paginator.num_pages
		currentPage = pageNum #当前页
		pageNumShown = 5  #显示页标个数

		context = Context({
			'obj_list':result_archive_list,
			'totalCount':totalCount,
			'numPerPage':numPerPage,
			'currentPage':currentPage,
			'pageNumShown':pageNumShown,
			'pageCount': pageCount,
			'archive_name':archive_name,
			"begin_time":begin_time,
			"end_time":end_time,
			"archive_attr": archive_attr,
			"archive_type": archive_type,
			"client_name":client_name,
			"archive_memo":archive_memo,
			"archive_operator":archive_operator,
			"client_clientid":client_clientid,
			'type':type,
			"obj_id":obj_id,
			"user":request.session.get("user",""),
			})
		if type=="3":
			if len(term_set)>0:
				terminal = term_set[0]
				statisticinfo=Archive.objects.filter(term=terminal).aggregate(sum_size =Sum("size"),total_count=Count("term"))
				context.update({
					'terminal':terminal,
					"sum_size":statisticinfo["sum_size"],
					"total_count":statisticinfo["total_count"],
				})
		return render_to_response("terminal/archive/archive_list.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()


@requires_login
def archive_add(request):
	"""
	"""
	jsondata ={
		"navTabId":"",
		"rel":"archiveBox",
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
			parent_id = request.POST.get("archive_parent.id","")
			parent_name = request.POST.get("archive_parent.name","")
			name = request.POST.get("name","")
			phone = request.POST.get("phone","")
			address = request.POST.get("address","")
			memo = request.POST.get("memo","")
			archive_id  = request.POST.get("id")
			if archive_id:
				#修改已存在的机构,暂时不支持所属机构的修改
				try:
					archive_id = int(archive_id)
					archive = Archive.objects.get(pk=archive_id)
					archive.name = name
					archive.phone = phone
					archive.memo= memo
					archive.save()
					archive_treenode =TreeNode.objects.get(type=1,obj_id=archive.id)
					archive_treenode.name = name
					archive_treenode.save()
					jsondata.update(STATUS_CODE["sucesss"])
					return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
				except ValueError:
					traceback.print_exc()
				except Exception:
					traceback.print_exc()
			else:
				#不存在的机构直接添加
				archive = Archive(name=name,parent_id=parent_id,phone=phone,address=address,memo=memo)
				archive.save()
				try:
					#找出树结点中新建机构的所属机构信息
					parentTreeNode = TreeNode.objects.get(type=1,obj_id=parent_id)
				except Exception:
					traceback.print_exc()
				else:
					#根据所属机构及提交信息构建树节点的机构信息
					newTreeNode = TreeNode(parent_id=parentTreeNode.id,name=name,type=1,obj_id=archive.id,level=parentTreeNode.level+1)
					newTreeNode.save()
					newTreeNode.link = parentTreeNode.link + str(newTreeNode.id)+"_"
					newTreeNode.save()
					jsondata.update(STATUS_CODE["sucesss"])
				return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')
				#		return HttpResponse(simplejson.dumps({"statusCode":200, "navTabId":request.POST.get('navTabId','newsindex'), "callbackType":request.POST.get('callbackType','closeCurrent'), "message":u'添加成功'}), mimetype='application/json')
		else:
			archive_id = request.GET.get("id","")
			context = Context({})
			if archive_id:
			#当修改机构时候,获取机构信息,返回页面
				try:
					archive_id = int(archive_id)
				except ValueError:
					raise Exception(u"获取id值错误")
				else:
					archive = Archive.objects.get(pk=archive_id)
					context = context.update({"archive":archive,})
			return render_to_response("terminal/archive/archive_add.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()
		jsondata.update(STATUS_CODE["failure"])
		return HttpResponse(simplejson.dumps(jsondata), mimetype='application/json')



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
@csrf_exempt
@requires_root
#未完成 1加入数据库日志,2删除录音文件
def archive_deletemany(request):
	"""
		批量删除记录
	"""
	try:
		if request.method =="POST":
			ids = request.POST.getlist("ids","")
			archives = Archive.objects.filter(id__in=ids)
			for  archive in archives:
				UserLog.objects.log_action(request,UserLog.DELE_OPT,UserLog.ARCH,archive)


			try:
				for  archive in archives:
					archive_path = archive.path
					if os.path.exists(archive_path):
						os.remove(archive_path)
						archive_path = archive_path.replace('.mp3','.attr')
						os.remove(archive_path)
					else:
						pass
			except:
				traceback.print_exc()

			archives.delete()

#			for org in orgs:
#				print org
		jsondata = {
			"statusCode":"200",
			"message":u"删除成功",
			"rel":"archiveBox",
		}
		return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')
	except:
		traceback.print_exc()
		jsondata = {
		"statusCode":"300",
		"message":u"删除失败",
		"rel":"archiveBox",
		}
	return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')

@csrf_exempt
@requires_login
@requires_root
def archieve_deleteFilter(request):
	pageNum = 1
	numPerPage = 10
	archive_name=""
	#	archive_phone=""
	#	archive_addr=""
	begin_time=""
	end_time=""
	archive_attr="-1"
	archive_type="-1"
	client_name=""
	archive_memo=""
	client_clientid=""
	archive_operator=""
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
			archive_name = request.POST.get("archive_name","")
			#			archive_phone = request.POST.get("archive_phone","")
			#			archive_addr = request.POST.get("archive_addr","")
			begin_time = request.POST.get("begin_time","")
			end_time = request.POST.get("end_time","")
			archive_attr = request.POST.get("archive_attr","-1")
			archive_type = request.POST.get("archive_type","-1")
			client_name = request.POST.get("client_name","")
			archive_memo = request.POST.get("archive_memo","")
			client_clientid = request.POST.get("client_clientid","")
			archive_operator = request.POST.get("archive_operator","")

			archive_queryset = Archive.objects.filter(term__in=term_set)
			if client_name:
				archive_queryset = archive_queryset.filter(Q(client__name__icontains=client_name) | Q(client__pinyin__icontains=client_name),
				)
			if client_clientid:
				archive_queryset = archive_queryset.filter(client__clientid__icontains=client_clientid)
			archive_queryset = archive_queryset.filter(memo__icontains=archive_memo)
			if archive_attr and archive_attr!="-1":
				archive_queryset = archive_queryset.filter(attr=archive_attr)
			#				print archive_type
			if archive_type and archive_type!="-1":
				archive_queryset = archive_queryset.filter(type=archive_type)
			if begin_time:
				archive_queryset = archive_queryset.filter(rectime__gte=begin_time)
			if end_time:
				archive_queryset = archive_queryset.filter(rectime__lte=end_time)
			if archive_operator:
				archive_queryset = archive_queryset.filter(operator__contains=archive_operator)

			for  archive in archive_queryset:
				UserLog.objects.log_action(request,UserLog.DELE_OPT,UserLog.ARCH,archive)

			allCount = len(archive_queryset)

			try:
				for  archive in archive_queryset:
					archive_path = archive.path
					if os.path.exists(archive_path):
						os.remove(archive_path)
						archive_path = archive_path.replace('.mp3','.attr')
						os.remove(archive_path)
					else:
						pass
			except:
				traceback.print_exc()

			archive_queryset.delete()
			jsondata = getJson(status=1,content="删除成功,删除记录"+str(allCount)+"条")
		else:
			jsondata = getJson(status=0,content="删除失败")
	except Exception,ex:
		print ex
		jsondata = getJson(status=0,content="删除出错")

	return HttpResponse(jsondata,mimetype = 'application/javascript')



@csrf_exempt
@requires_login
@requires_root
def archive_delete(request):
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
					archive = Archive.objects.get(pk=id)

					#			for  archive in archives:
					try:
						archive_path = archive.path
						if os.path.exists(archive_path):
							os.remove(archive_path)
							archive_path = archive_path.replace('.mp3','.attr')
						os.remove(archive_path)
					except:
						traceback.print_exc()

					archive.delete()
					jsondata = {
						"statusCode":"200",
						"message":u"删除成功",
						"navTabId":"",
						"rel":"archiveBox",
					}

				return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')

	except:
		traceback.print_exc()
		jsondata = {
			"statusCode":"300",
			"message":u"删除失败",
			"rel":"archiveBox",
			}
	return HttpResponse(simplejson.dumps(jsondata),mimetype = 'application/javascript')

@requires_login
def archive_play(request):
	jsondata = {
#		"statusCode":"200",
#		"message":u"删除成功",
#		"navTabId":"",
#		"rel":"archiveBox",
#		"callbackType":"",
#		"forwardUrl":"",
#		"confirmMsg":""
	}
	try:
		id = request.GET.get("id","")
		if id:
			id = int(id)
			archive = Archive.objects.get(pk=id)
			UserLog.objects.log_action(request,UserLog.PLAY_OPT,UserLog.ARCH,archive)
			context = Context({
				"archive":archive,
			})
			src_pathname = archive.path
			#print 'play archive:',archive.path
#			src_pathname = r"D:\project_now\OurTomorrowLikeTheSun\SVN\leadtel_audio\trunk\src\bocm_audio\audio\static\js\audiojs\audiofinal.mp3"
			print 'play archive:',archive.path
			if os.path.exists(src_pathname) and os.path.isfile(src_pathname):
				path,filename = os.path.split(src_pathname)
#				now = datetime.datetime.now()
#				nowstr = now.strftime("%Y%m%d%H%M%S")
				newDir = settings.MEDIA_ROOT
				newfilepath = newDir + "/"+ filename

				if os.path.exists(newDir) and os.path.isdir(newDir):
					pass
				else:
					os.mkdir(newDir)
				# newfilepath = newDir + "/"+ archive.digest
				if os.path.exists(newfilepath):
					pass
				else:
					shutil.copyfile(src_pathname,newfilepath)
				#-- begin --
				# convert spx to mp3
				# import storeadapter.convert
				# mp3file = storeadapter.convert.spx_convert_mp3(newfilepath)
				#不用转换spx到mp3 ~~ 2013.10.9
				mp3file = newfilepath
				filename = os.path.split(mp3file)[1]
				print 'play mp3file:',mp3file
				#-- end --
				media_url = filename.replace('#','%23') #转移处理
				context.update({"media_url":media_url})
				return render_to_response("terminal/archive/playArchive.html",context,context_instance=RequestContext(request))
			else:
				return HttpResponse(u"文件可能不存在或者被删除")
	except Exception,e:
		traceback.print_exc()
		return HttpResponse(u"文件可能不存在或者被删除")

@requires_login
def archive_download(request):
	try:
		id = request.GET.get("id","")
		if id:
			id = int(id)
			archive = Archive.objects.get(pk=id)
			UserLog.objects.log_action(request,UserLog.DOWN_OPT,UserLog.ARCH,archive)
			context = Context({
				"archive":archive,
				})
			src_pathname = archive.path
#			src_pathname = r"D:\project_now\OurTomorrowLikeTheSun\SVN\leadtel_audio\trunk\src\bocm_audio\audio\static\js\audiojs\audiofinal.mp3"
			if os.path.exists(src_pathname) and os.path.isfile(src_pathname):
				path,filename = os.path.split(src_pathname)
				# now = datetime.datetime.now()
				# nowstr = now.strftime("%Y%m%d%H%M%S")
				# newfilename = nowstr+".mp3"
				newfilename = filename                          #下载文件名直接取spx文件的名称
				response = HttpResponse(mimetype="audio/x-mpeg")
				response['Content-Disposition'] = 'attachment; filename='+newfilename
				response.write(open(src_pathname, "rb").read())
				response.close()
				return response
			else:
				return HttpResponse(u"下载失败,文件可能不存在或者被删除")
		else:
			return HttpResponse(u"下载失败,文件可能不存在或者被删除")
	except Exception,e:
		traceback.print_exc()
		return HttpResponse(u"下载失败,文件可能不存在或者被删除")

@requires_login
def archieves_export(request):
	try:
		if request.method == "GET":
			UserLog.objects.log_action(request,UserLog.EXPORT_OPT,UserLog.ARCH)
			type = request.GET.get("type","").strip()
			obj_id = request.GET.get("obj_id","").strip()
			begin_time = request.GET.get("begin_time","")
			end_time = request.GET.get("end_time","")
			archive_attr = request.GET.get("archive_attr","")
			client_name = request.GET.get("client_name","")
			archive_memo = request.GET.get("archive_memo","")
			client_clientid = request.GET.get("client_clientid","")
			archive_operator = request.GET.get("archive_operator","")
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
			archive_queryset = Archive.objects.filter(term__in=term_set)
			if client_name:
				archive_queryset = archive_queryset.filter(Q(client__name__icontains=client_name) | Q(client__pinyin__icontains=client_name),
				)
			if client_clientid:
				archive_queryset = archive_queryset.filter(client__clientid__icontains=client_clientid)
			archive_queryset = archive_queryset.filter(memo__icontains=archive_memo)
			if archive_attr and archive_attr!="-1":
				archive_queryset = archive_queryset.filter(attr=archive_attr)
			if begin_time:
				archive_queryset = archive_queryset.filter(rectime__gte=begin_time)
			if end_time:
				archive_queryset = archive_queryset.filter(rectime__lte=end_time)
			if archive_operator:
				archive_queryset = archive_queryset.filter(operator__contains=archive_operator)
			now = datetime.datetime.now()
			filename = now.strftime("%Y%m%d%H%M%S")+".xls"
			filename = u"录音资料.xls"
			filename = filename.encode("gbk")
			response = HttpResponse(mimetype="application/ms-excel")
			response['Content-Disposition'] = 'attachment; filename='+filename
			wb = xlwt.Workbook()
			ws = wb.add_sheet(u'录音资料')
			ws.write(0,0,u"所属终端")
			ws.write(0,1,u"电话号码")
			ws.write(0,2,u"文件名称")
			ws.write(0,3,u"文件大小")
			ws.write(0,4,u"录音时间")
			ws.write(0,5,u"时长")
			ws.write(0,6,u"上传时间")
			ws.write(0,7,u"去电属性")
			ws.write(0,8,u"客户名称")
			ws.write(0,9,u"通话类型")
			ws.write(0,10,u"说明")
			ws.write(0,11,u"产品id")
			ws.write(0,12,u"操作员")
			ws.write(0,13,u"文件校验码")
			row = 1
			for archive in archive_queryset:
				ws.write(row,0,archive.term.user)
				ws.write(row,1,archive.phone)
				ws.write(row,2,archive.name)
				ws.write(row,3,intB2ReadableStr(archive.size))
				ws.write(row,4,archive.rectime.strftime("%Y-%m-%d"))
				ws.write(row,5,formatTimeLength(archive.duration))
				ws.write(row,6,archive.uptime.strftime("%Y-%m-%d"))
				ws.write(row,7,archive.get_attr_display())
				if archive.client:
					ws.write(row,8,archive.client.name)
				else:
					ws.write(row,8,"")
				ws.write(row,9,archive.get_type_display())
				ws.write(row,10,archive.memo)
				ws.write(row,11,archive.productid)
				ws.write(row,12,archive.operator)
				ws.write(row,13,archive.spx_digest)
				row +=1
			wb.save(response)
			return response

	except Exception,e:
		traceback.print_exc()

