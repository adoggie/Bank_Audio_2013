__author__ = 'daitr'
#-*-coding:utf-8-*-

import traceback
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.template import Context,RequestContext
from django.db import connection

from audio.constants import STATUS_CODE
from audio.account import  *
from utils.pageHandle import getPage
from utils.formatTime import formatTimeLength
from audio.models import *
from utils.MyEncoder import getJson
import xlwt
import logging
log = logging.getLogger('audio_logger')

def manager_statistic_search(**args):
	parent_org = args.get("parent_org")
	begin_time = args.get("begin_time")
	end_time = args.get("end_time")
	paras =(parent_org.link+"%%",begin_time,end_time)
	all_result =[]
	cursor = connection.cursor()
	cursor.execute("""
					select employee,"term","times_sum","times_in","times_out","times_record","times_miss","times_lt2min","times_nor","times_sell","times_other","time_sum",o1.name
					from
					(select t1.employee,t1.user as "term",count(t1.id) as "times_sum",sum(case attr when 0  then 1 else 0 end) as "times_in",
					sum(case attr when 1  then 1 else 0 end) as "times_out",
					sum(case attr when 2  then 1 else 0 end) as "times_record",sum(case attr when 3  then 1 else 0 end) as "times_miss",
					sum(case when  duration<120  then 1 else 0 end) as "times_lt2min",
					sum(case type when 1  then 1 else 0 end) as "times_nor",
					sum(case type when 2  then 1 else 0 end) as "times_sell",
					sum(case type when 3  then 1 else 0 end) as "times_other",
					sum(duration) as "time_sum",
					t1.org_id as org_id
					from audio_archive a1,audio_terminal t1
					where t1.id = a1.term_id   and
						t1.org_id in (
							select o2.id
							from audio_organization o2
							where o2.link like %s
						)
						and a1.rectime>%s and a1.rectime<%s
					group by t1.id,t1.employee,t1.user,t1.org_id) as rt1,audio_organization o1
					where o1.id= rt1.org_id
						"""
		,paras)
	query_result = cursor.fetchall()
	sum_ ={}
	sum_['times_sum']=0
	sum_['times_sum'],sum_['times_in'],sum_['times_out'],sum_['times_record'],\
	sum_['times_miss'],sum_['times_lt2min'],sum_['times_nor'],sum_['times_sell'],\
	sum_['times_other'],sum_['time_sum']=(0,0,0,0,0,0,0,0,0,0)
	avg_ ={}
	avg_['times_sum'],avg_['times_in'],avg_['times_out'],avg_['times_record'],\
	avg_['times_miss'],avg_['times_lt2min'],avg_['times_nor'],avg_['times_sell'],\
	avg_['times_other'],avg_['time_sum']=(0,0,0,0,0,0,0,0,0,0)
	if len(query_result)>0:
		for row in query_result:
			oneResult ={}
			oneResult['employee'] = row[0]
			oneResult['term'] =  row[1]

			oneResult['times_sum'] =  row[2]
			sum_['times_sum'] += oneResult['times_sum']

			oneResult['times_in'] = row[3]
			sum_['times_in'] += oneResult['times_in']

			oneResult['times_out'] = row[4]
			sum_['times_out'] += oneResult['times_out']

			oneResult['times_record'] = row[5]
			sum_['times_record'] += oneResult['times_record']

			oneResult['times_miss'] = row[6]
			sum_['times_miss'] += oneResult['times_miss']

			oneResult['times_lt2min'] = row[7]
			sum_['times_lt2min'] += oneResult['times_lt2min']

			oneResult['times_nor'] = row[8]
			sum_['times_nor'] += oneResult['times_nor']

			oneResult['times_sell'] = row[9]
			sum_['times_sell'] += oneResult['times_sell']

			oneResult['times_other'] = row[10]
			sum_['times_other'] += oneResult['times_other']

			oneResult['time_sum'] = row[11]
			sum_['time_sum'] += oneResult['time_sum']

			oneResult['org_name'] = row[12]

			all_result.append(oneResult)
		avg_['times_sum'] += float(sum_['times_sum'])/len(all_result)
		avg_['times_in'] += float(sum_['times_in'])/len(all_result)
		avg_['times_out'] += float(sum_['times_out'])/len(all_result)
		avg_['times_record'] += float(sum_['times_record'])/len(all_result)
		avg_['times_miss'] += float(sum_['times_miss'])/len(all_result)
		avg_['times_lt2min'] += float(sum_['times_lt2min'])/len(all_result)
		avg_['times_nor'] += float(sum_['times_nor'])/len(all_result)
		avg_['times_sell'] += float(sum_['times_sell'])/len(all_result)
		avg_['times_other'] += float(sum_['times_other'])/len(all_result)
		avg_['time_sum'] += float(sum_['time_sum'])/len(all_result)
	return all_result,avg_,sum_

@csrf_exempt
@requires_login
def manager_statistics(request):
		'''
	  根据当前用户所属的机构来确定构建机构树的根结点
	   '''
		try:
			#获取根机构结点
			orgs_tree = TreeNode.objects.filter(type=1,link__startswith="1_")
			context=({
				'treenode_list':orgs_tree,
				})
			return render_to_response("statistics/manager_statistics.html",context,context_instance=RequestContext(request))
		except:
			traceback.print_exc()

@requires_login
def mana_statis_export(request):
	try:
		if request.method == "GET":
			UserLog.objects.log_action(request,UserLog.EXPORT_OPT,UserLog.CLIENT)
			begin_time = request.GET.get("begin_time","")
			end_time = request.GET.get("end_time","")
			tree_select_org_idstr = request.GET.get("tree_select_org_id","")
			tree_select_org_id = int(tree_select_org_idstr)
			parent_org = Organization.objects.get(id=tree_select_org_id)
			all_result,avg_,sum_ = manager_statistic_search(parent_org=parent_org,begin_time=begin_time,end_time=end_time)
			#			now = datetime.now()
			#			filename = now.strftime("%Y%m%d%H%M%S")+".xls"
			filename = u"客户经理统计.xls"
			filename = filename.encode("gbk")
			response = HttpResponse(mimetype="application/ms-excel")
			response['Content-Disposition'] = 'attachment; filename='+filename
			wb = xlwt.Workbook()
			ws = wb.add_sheet(u'客户经理统计')
			if len(all_result)>0:
				ws.write(0,0,u"客户经理名称")
				ws.write(0,1,u"所属话机")
				ws.write(0,2,u"所属机构")
				ws.write(0,3,u"与客户通话次数")
				ws.write(0,4,u"呼入次数")
				ws.write(0,5,u"呼出次数")
				ws.write(0,6,u"面谈次数")
				ws.write(0,7,u"未接次数")
				ws.write(0,8,u"低于两分钟通话次数")
				ws.write(0,9,u"通话类型(日常沟通)")
				ws.write(0,10,u"通话类型(销售)")
				ws.write(0,11,u"通话类型(其他)")
				ws.write(0,12,u"总通话时长")
				row = 1
				for result in all_result:
					ws.write(row,0,result.get("employee"))
					ws.write(row,1,result.get("term"))
					ws.write(row,2,result.get("org_name"))
					ws.write(row,3,result.get("times_sum"))
					ws.write(row,4,result.get("times_in"))
					ws.write(row,5,result.get("times_out"))
					ws.write(row,6,result.get("times_record"))
					ws.write(row,7,result.get("times_miss"))
					ws.write(row,8,result.get("times_lt2min"))
					ws.write(row,9,result.get("times_nor"))
					ws.write(row,10,result.get("times_sell"))
					ws.write(row,11,result.get("times_other"))
					ws.write(row,12,formatTimeLength(result.get("time_sum")))
					row +=1
				ws.write(row,0,u"平均值")
				ws.write(row,2,avg_.get("org_name"))
				ws.write(row,3,avg_.get("times_sum"))
				ws.write(row,4,avg_.get("times_in"))
				ws.write(row,5,avg_.get("times_out"))
				ws.write(row,6,avg_.get("times_record"))
				ws.write(row,7,avg_.get("times_miss"))
				ws.write(row,8,avg_.get("times_lt2min"))
				ws.write(row,9,avg_.get("times_nor"))
				ws.write(row,10,avg_.get("times_sell"))
				ws.write(row,11,avg_.get("times_other"))
				ws.write(row,12,formatTimeLength(avg_.get("time_sum")))
				row+=1
				ws.write(row,0,u"总和")
				ws.write(row,2,sum_.get("org_name"))
				ws.write(row,3,sum_.get("times_sum"))
				ws.write(row,4,sum_.get("times_in"))
				ws.write(row,5,sum_.get("times_out"))
				ws.write(row,6,sum_.get("times_record"))
				ws.write(row,7,sum_.get("times_miss"))
				ws.write(row,8,sum_.get("times_lt2min"))
				ws.write(row,9,sum_.get("times_nor"))
				ws.write(row,10,sum_.get("times_sell"))
				ws.write(row,11,sum_.get("times_other"))
				ws.write(row,12,formatTimeLength(sum_.get("time_sum")))

			wb.save(response)
			return response

	except Exception,e:
		traceback.print_exc()

@csrf_exempt
@requires_login
def mana_statis_list(request):
	#分页
	pageNum = 1
	numPerPage = 10
	#查询字段
	begin_time=""
	end_time=""
	root_org_id =-1
	try:
		if request.method == "POST":
			begin_time = request.POST.get("begin_time","")
			end_time = request.POST.get("end_time","")

			pageNumstr = request.POST.get("pageNum",1) #  当前页
			numPerPagestr = request.POST.get("numPerPage",10)
			tree_select_org_idstr = request.POST.get("tree_select_org_id","")
			try:
				pageNum=int(pageNumstr)
				numPerPage = int(numPerPagestr)
				tree_select_org_id = int(tree_select_org_idstr)
				root_org_id = int(tree_select_org_id)
			except ValueError,e:
				raise Http404()
		else:
			date_begin = datetime.date.today()
			date_end = date_begin + datetime.timedelta(days=1)

			begin_time = date_begin.strftime("%Y-%m-%d %H:%M:%S")
			end_time = date_end.strftime("%Y-%m-%d %H:%M:%S")

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
#			children_org_queryset = Organization.objects.filter(link__startswith=parent_org.link)
#			#print user_user,user_name,user_addr
#			user_list = User.objects.filter(org__in=children_org_queryset,user__contains=user_user)
			all_result,avg_,sum_ = manager_statistic_search(parent_org=parent_org,begin_time=begin_time,end_time=end_time)
			onePageresults = getPage(all_result,numPerPage,pageNum)

			paginator = onePageresults.paginator
			object_list = onePageresults.object_list #要显示的记录

			totalCount = paginator.count #总数量
			numPerPage = paginator.per_page #每页显示的数量
			pageCount = paginator.num_pages
			currentPage = pageNum #当前页
			pageNumShown = 5  #显示页标个数

			context = Context({
				'obj_list':object_list,
				'totalCount':totalCount,
				'numPerPage':numPerPage,
				'currentPage':currentPage,
				'pageNumShown':pageNumShown,
				'pageCount': pageCount,
				"tree_select_org_id":tree_select_org_id,
				"begin_time":begin_time,
				"end_time":end_time,
				"sum_":sum_,
				"avg_":avg_,
				})
			return render_to_response("statistics/mana_statis_list.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()


@csrf_exempt
@requires_login
def client_statistics(request):
	'''
	   根据当前用户所属的机构来确定构建机构树的根结点
		'''
	try:
		#获取根机构结点
		orgs_tree = TreeNode.objects.filter(type=1,link__startswith="1_")
		context=({
			'treenode_list':orgs_tree,
			})
		return render_to_response("statistics/client_statistics.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()

def client_statistic_search(**args):
	parent_org = args.get("parent_org")
	begin_time = args.get("begin_time")
	end_time = args.get("end_time")
	paras =(parent_org.link+"%%",begin_time,end_time)
	all_result =[]
	cursor = connection.cursor()
	cursor.execute("""
				select c1.clientid,c1.name,times_call,duration_call,count_manager
				from
				(select a1.client_id,count(a1.client_id) as "times_call",sum(duration) as "duration_call",count(DISTINCT  a1.term_id) as "count_manager"
				from audio_archive a1,audio_terminal t1
				where t1.id = a1.term_id and client_id is not null
					and t1.org_id in (
						select o1.id
						from audio_organization o1
						where o1.link like %s
					)
					and a1.rectime>%s and a1.rectime<%s
				group by client_id) as rt1,audio_client as c1
				where rt1.client_id = c1.id
					"""
		,paras)
	sum_ ={}
	sum_['times_call'],sum_['duration_call'],sum_['count_manager'],sum_['call_time_avg']=(0,0,0,0)
	avg_ ={}
	avg_['times_call'],avg_['duration_call'],avg_['count_manager'],avg_['call_time_avg']=(0,0,0,0)
	query_result = cursor.fetchall()
	if len(query_result)>0:
		for row in query_result:
			oneResult ={}

			oneResult['client_id'] = row[0]
			oneResult['client_name'] =  row[1]

			oneResult['times_call'] =  row[2]
			sum_['times_call'] += oneResult['times_call']

			oneResult['duration_call'] = row[3]
			sum_['duration_call'] += oneResult['duration_call']

			oneResult['count_manager'] = row[4]
			sum_['count_manager'] += oneResult['count_manager']

			oneResult['call_time_avg'] = float(oneResult['duration_call'])/oneResult['times_call']
			sum_['call_time_avg'] += oneResult['call_time_avg']

			all_result.append(oneResult)
		if len(query_result)>0:
			avg_['times_call'] += float(sum_['times_call'])/len(query_result)
			avg_['call_time_avg'] += float(sum_['call_time_avg'])/len(query_result)
			avg_['count_manager'] += float(sum_['count_manager'])/len(query_result)
			avg_['duration_call'] += float(sum_['duration_call'])/len(query_result)

	return all_result,avg_,sum_

@csrf_exempt
@requires_login
def client_statis_list(request):
	#分页
	pageNum = 1
	numPerPage = 10
	#查询字段
	begin_time=""
	end_time=""
	root_org_id =-1
	try:
		if request.method == "POST":
			begin_time = request.POST.get("begin_time","")
			end_time = request.POST.get("end_time","")

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
			date_begin = datetime.date.today()
			date_end = date_begin + datetime.timedelta(days=1)

			begin_time = date_begin.strftime("%Y-%m-%d %H:%M:%S")
			end_time = date_end.strftime("%Y-%m-%d %H:%M:%S")

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
		#			children_org_queryset = Organization.objects.filter(link__startswith=parent_org.link)
		#			#print user_user,user_name,user_addr
		#			user_list = User.objects.filter(org__in=children_org_queryset,user__contains=user_user)
			limit = numPerPage
			offset = (pageNum-1)*numPerPage
			paras =(parent_org.link+"%%",begin_time,end_time)
			all_result =[]
			cursor = connection.cursor()
			cursor.execute("""
				select c1.clientid,c1.name,times_call,duration_call,count_manager
				from
				(select a1.client_id,count(a1.client_id) as "times_call",sum(duration) as "duration_call",count(DISTINCT  a1.term_id) as "count_manager"
				from audio_archive a1,audio_terminal t1
				where t1.id = a1.term_id and client_id is not null
					and t1.org_id in (
						select o1.id
						from audio_organization o1
						where o1.link like %s
					)
					and a1.rectime>%s and a1.rectime<%s
				group by client_id) as rt1,audio_client as c1
				where rt1.client_id = c1.id
					"""
				,paras)
			sum_ ={}
			sum_['times_call'],sum_['duration_call'],sum_['count_manager'],sum_['call_time_avg']=(0,0,0,0)
			avg_ ={}
			avg_['times_call'],avg_['duration_call'],avg_['count_manager'],avg_['call_time_avg']=(0,0,0,0)
			query_result = cursor.fetchall()
			for row in query_result:
				oneResult ={}

				oneResult['client_id'] = row[0]
				oneResult['client_name'] =  row[1]

				oneResult['times_call'] =  row[2]
				sum_['times_call'] += oneResult['times_call']

				oneResult['duration_call'] = row[3]
				sum_['duration_call'] += oneResult['duration_call']

				oneResult['count_manager'] = row[4]
				sum_['count_manager'] += oneResult['count_manager']

				oneResult['call_time_avg'] = float(oneResult['duration_call'])/oneResult['times_call']
				sum_['call_time_avg'] += oneResult['call_time_avg']

				all_result.append(oneResult)
			if len(query_result)>0:
				avg_['times_call'] += float(sum_['times_call'])/len(query_result)
				avg_['call_time_avg'] += float(sum_['call_time_avg'])/len(query_result)
				avg_['count_manager'] += float(sum_['count_manager'])/len(query_result)


			onePageresults = getPage(all_result,numPerPage,pageNum)

			paginator = onePageresults.paginator
			object_list = onePageresults.object_list #要显示的记录

			totalCount = paginator.count #总数量
			numPerPage = paginator.per_page #每页显示的数量
			pageCount = paginator.num_pages
			currentPage = pageNum #当前页
			pageNumShown = 5  #显示页标个数

			context = Context({
				'obj_list':object_list,
				'totalCount':totalCount,
				'numPerPage':numPerPage,
				'currentPage':currentPage,
				'pageNumShown':pageNumShown,
				'pageCount': pageCount,
				"tree_select_org_id":tree_select_org_id,
				"begin_time":begin_time,
				"end_time":end_time,
				"sum_":sum_,
				"avg_":avg_,

				})
			return render_to_response("statistics/client_statis_list.html",context,context_instance=RequestContext(request))
	except:
		traceback.print_exc()

@requires_login
def client_statis_export(request):
	try:
		if request.method == "GET":
			UserLog.objects.log_action(request,UserLog.EXPORT_OPT,UserLog.CLIENT)
			begin_time = request.GET.get("begin_time","")
			end_time = request.GET.get("end_time","")
			tree_select_org_idstr = request.GET.get("tree_select_org_id","")
			tree_select_org_id = int(tree_select_org_idstr)
			parent_org = Organization.objects.get(id=tree_select_org_id)
			all_result,avg_,sum_ = client_statistic_search(parent_org=parent_org,begin_time=begin_time,end_time=end_time)
			#			now = datetime.now()
			#			filename = now.strftime("%Y%m%d%H%M%S")+".xls"
			filename = u"客户统计.xls"
			filename = filename.encode("gbk")
			response = HttpResponse(mimetype="application/ms-excel")
			response['Content-Disposition'] = 'attachment; filename='+filename
			wb = xlwt.Workbook()
			ws = wb.add_sheet(u'客户统计')
			if len(all_result)>0:
				ws.write(0,0,u"客户ID号")
				ws.write(0,1,u"客户姓名")
				ws.write(0,2,u"与客户经理通话次数")
				ws.write(0,3,u"平均通话时间")
				ws.write(0,4,u"通话的客户经理人数")
				row = 1
				for result in all_result:
					ws.write(row,0,result.get("client_id"))
					ws.write(row,1,result.get("client_name"))
					ws.write(row,2,result.get("times_call"))
					ws.write(row,3,formatTimeLength(result.get("duration_call")/result.get("times_call")))
					ws.write(row,4,result.get("count_manager"))
					row +=1
				ws.write(row,0,u"平均值")
				ws.write(row,2,avg_.get("times_call"))
				ws.write(row,3,formatTimeLength(avg_.get("duration_call")))
				ws.write(row,4,avg_.get("count_manager"))
				row+=1
				ws.write(row,0,u"总和")
				ws.write(row,2,sum_.get("times_call"))
				ws.write(row,3,formatTimeLength(sum_.get("duration_call")))
				ws.write(row,4,sum_.get("count_manager"))

			wb.save(response)
			return response

	except Exception,e:
		traceback.print_exc()