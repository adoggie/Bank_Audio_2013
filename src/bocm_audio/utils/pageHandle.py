# -*- coding: UTF-8 -*-
'''
Created on 2012-3-21

@author: daitr
'''
from django.core.paginator import Paginator, InvalidPage, EmptyPage

'''分页处理
'''
def devidePage(request,list,pageCount=10):
    paginator = Paginator(list, pageCount) # Show 25 contacts per page
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        pass
#    page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        OnepageResult = paginator.page(page)
    except (EmptyPage, InvalidPage):
        OnepageResult = paginator.page(paginator.num_pages)
    return OnepageResult

def getPage(list,pageCount,currentPage):
	paginator = Paginator(list, pageCount)
	page = paginator.page(currentPage)
	return page

'''
通过当前页和每页的数量获取单页的对象及其分页参数
@currentPage当前页
@numPerPage每页的数量
returnPage对象,
'''
def getPage(object_list,numPerPage,currentPage):
	paginator = Paginator(object_list, numPerPage)
	try:
		OnepageResult = paginator.page(currentPage)
	except (EmptyPage, InvalidPage):
		OnepageResult = paginator.page(paginator.num_pages)
	return OnepageResult