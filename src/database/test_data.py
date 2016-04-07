# -*- coding: utf-8 -*-
import sys,os
import traceback,threading,time,struct,os,os.path,shutil,distutils.dir_util,array,base64,zlib,struct,binascii
import datetime
import json,hashlib,base64
from django.http import *
from django.db import transaction

from django.shortcuts import render_to_response



from django.views.decorators.csrf import csrf_exempt


os.environ["DJANGO_SETTINGS_MODULE"] = "audio.settings"

import audio.core.models as cm



cm.TreeNode.objects.all().delete()

cm.Organization.objects.all().delete()
cm.User.objects.all().delete()
cm.Terminal.objects.all().delete()
cm.Archive.objects.all().delete()
cm.SysSettings.objects.all().delete()


#root begin
org = cm.Organization()
org.name = u'交通银行总行'
org.save()
org.link = str(org.id)+'_'
org.save()

org_root_tr = cm.TreeNode()
org_root_tr.parent = None
org_root_tr.name = org.name
org_root_tr.type = 1 # org
org_root_tr.obj_id = org.id
org_root_tr.level = 1
org_root_tr.save()

org_root_tr.link = str(org_root_tr.id)+"_"
org_root_tr.save()

#user root
user = cm.User()
user.org = org
user.user ='root'
user.passwd='111111'
user.name='root'
user.rights=0
user.save()

utr = cm.TreeNode()
utr.parent = org_root_tr
utr.name = user.user
utr.type = 2 # org
utr.obj_id = user.id
utr.level = org_root_tr.level+1
utr.save()
utr.link = org_root_tr.link + str(utr.id)+"_"
utr.save()

#root end ---


#--- branch begin ---
org1 = cm.Organization()
org1.name = u'上海交通银行分行'
org1.parent = org
org1.save()
org1.link = org.link+ str(org1.id)+'_'
org1.save()

ogr_ttr = cm.TreeNode()
ogr_ttr.parent = org_root_tr
ogr_ttr.name = org1.name
ogr_ttr.type = 1 # org
ogr_ttr.obj_id = org1.id
ogr_ttr.level = org_root_tr.level+1
ogr_ttr.save()
ogr_ttr.link = org_root_tr.link + str(ogr_ttr.id)+"_"
ogr_ttr.save()

# -- terminal begin ---
term = cm.Terminal()
term.org = org1
term.user = 'test'
term.passwd = '111111'
term.createtime = datetime.datetime.now()
term.regtime = datetime.datetime.now()
term.creator = user
term.save()

ttr = cm.TreeNode()
ttr.parent = ogr_ttr
ttr.name = term.user
ttr.type = 3 # org
ttr.obj_id = term.id
ttr.level = ogr_ttr.level+1
ttr.save()
ttr.link = ogr_ttr.link + str(ttr.id)+"_"
ttr.save()


#
# org11 = cm.Organization()
# org11.name = u'交通银行川沙支行'
# org11.parent = org1
# org11.save()
#
# org12 = cm.Organization()
# org12.name = u'交通银行周浦支行'
# org12.parent = org1
# org12.save()
#
# user = cm.User()
# user.org = org
# user.user ='test'
# user.passwd='111111'
# user.name='test user1'
# user.rights=0xffff
# user.save()
#
#
# term = cm.Terminal()
# term.org = org11
# term.user = 'test'
# term.passwd = '111111'
# term.createtime = datetime.datetime.now()
# term.regtime = datetime.datetime.now()
# term.creator = user
# term.save()

kvs={
	'terminal_version':'0.1.0.0',
	'terminal_package':'c:/leadtel_term_0.1.0.0.upx',
	'store_path': 'c:/leadtel/incoming'
}

for k,v in kvs.items():
	settings = cm.SysSettings()
	settings.key = k
	settings.value = v
	settings.save()

# print term