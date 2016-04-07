# -*- coding: utf-8 -*-

#init_terms.py
# 导入xls中定义的终端设备信息

import sys,os
import traceback,threading,time,struct,os,os.path,shutil,distutils.dir_util,array,base64,zlib,struct,binascii
import datetime
import json,hashlib,base64
import xlrd

# set DJANGO_SETTINGS_MODULE=bocm_audio.settings
os.putenv("DJANGO_SETTINGS_MODULE","bocm_audio.settings")


from django.http import *
from django.db import transaction


from django.shortcuts import render_to_response



from django.views.decorators.csrf import csrf_exempt


#os.environ["DJANGO_SETTINGS_MODULE"] = "audio.settings"

import audio.models as cm

def generate_passwd(userRow):
	return ''

def init_terms:
	try:
		root = cm.User.objects.get(user='root')

		book = xlrd.open_workbook(xlsfile)
		sheet = book.sheet_by_index(0)
		row = 0
		if sheet.cell_value(0,0)!=u'机构名称':
			return False
		row = 1
		result=[]
#		print sheet.nrows
		for r in range(row,sheet.nrows):
			values = sheet.row_values(r)
			for n in range(len(values)):
				if values[n] == None:
					values[n]=''
				elif type(values[n]) == type(u''):
					values[n] = values[n].encode('utf-8')
				else:
					values[n] = str(values[n])
			result.append(values)

		countForInserted = 0
		for r in result:
			if not r[2]: #user is null
				continue
			rs = cm.Organization.objects.filter(name=r[1])
			if not rs:
				print 'org2 not found!'
				continue
			org2 = rs[0]
			org1 = org2.parent
			if not org1 or org1.name != r[0]:
				print 'name of org1 not matched',repr(r[0])
				continue
			rs = cm.Terminal.objects.filter(user=r[2])
			if  rs: # 存在相同账号的设备
				continue

			passwd = generate_passwd(r)
			term = cm.Terminal()
			term.org = org2
			term.user = r[2]
			term.passwd = passwd
			term.createtime = datetime.datetime.now()
			term.regtime = datetime.datetime.now()
			term.creator = root
			term.save()

			tr_org = cm.TreeNode.objects.get(obj_id=org2.id)
			ttr = cm.TreeNode()
			ttr.parent = tr_org
			ttr.name = term.user
			ttr.type = 3 # org
			ttr.obj_id = term.id
			ttr.level = tr_org.level+1
			ttr.save()
			ttr.link = tr_org.link + str(ttr.id)+"_"
			ttr.save()


			countForInserted+=1
		print '%s objects be handed in !'%countForInserted
	except:
		traceback.print_exc()



#user root
# user = cm.User()
# user.org = org
# user.user ='root'
# user.passwd='111111'
# user.name='root'
# user.rights=0
# user.save()
#
# utr = cm.TreeNode()
# utr.parent = org_root_tr
# utr.name = user.user
# utr.type = 2 # org
# utr.obj_id = user.id
# utr.level = org_root_tr.level+1
# utr.save()
# utr.link = org_root_tr.link + str(utr.id)+"_"
# utr.save()

#root end ---


#--- branch begin ---
# org1 = cm.Organization()
# org1.name = u'上海交通银行分行'
# org1.parent = org
# org1.save()
# org1.link = org.link+ str(org1.id)+'_'
# org1.save()
#
# ogr_ttr = cm.TreeNode()
# ogr_ttr.parent = org_root_tr
# ogr_ttr.name = org1.name
# ogr_ttr.type = 1 # org
# ogr_ttr.obj_id = org1.id
# ogr_ttr.level = org_root_tr.level+1
# ogr_ttr.save()
# ogr_ttr.link = org_root_tr.link + str(ogr_ttr.id)+"_"
# ogr_ttr.save()
#
# # -- terminal begin ---
# term = cm.Terminal()
# term.org = org1
# term.user = 'test'
# term.passwd = '111111'
# term.createtime = datetime.datetime.now()
# term.regtime = datetime.datetime.now()
# term.creator = user
# term.save()
#
# ttr = cm.TreeNode()
# ttr.parent = ogr_ttr
# ttr.name = term.user
# ttr.type = 3 # org
# ttr.obj_id = term.id
# ttr.level = ogr_ttr.level+1
# ttr.save()
# ttr.link = ogr_ttr.link + str(ttr.id)+"_"
# ttr.save()



# print term
