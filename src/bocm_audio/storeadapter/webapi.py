# -*- coding: utf-8 -*-

'''
2013.7.8
	1. login() 增加appver参数； 记录登陆时间

'''

import sys,os
import traceback,threading,time,struct,os,os.path,shutil,distutils.dir_util,array,base64,zlib,struct,binascii
import datetime
import json,hashlib,base64
from django.http import *
from django.db import transaction

from django.shortcuts import render_to_response
import cipher,pickle
from base import *

from django.views.decorators.csrf import csrf_exempt

from base import WebCallReturn as CallReturn
#import database.audio.core.models as cm
import audio.models as cm
import utils

#print 'sssss'*20
print 'storeadpater.webapi be loaded..'

@csrf_exempt
def login(r):
	cr = SuccCallReturn()

	try:
		user = GET(r,'user')
		passwd = GET(r,'passwd')
		appver = GET(r,'appver','')
		#print user,passwd
		if not user or not passwd:
			return WebCallReturn(ecode= AppErrors.PARAM_NOT_AVAILABLE).httpResponse()
		rs = cm.Terminal.objects.filter(user=user,passwd=passwd)
		if not rs:
			return FailCallReturn(ecode=AppErrors.AUTH_FAILED).httpResponse()

		r = rs[0]

		term = {'id':r.id,'user':r.user,'login_time':int(time.time())}
		token = cipher.encryptToken(term)
		cr.assign({'token':token})
		print 'login succ:',term
		r.regtime = datetime.datetime.now()
		r.appver = appver
		r.save()
	except:
		cr = FailCallReturn()
	return cr.httpResponse()

@csrf_exempt
def updateTermInfo(r):
	'''
		更新终端附属信息
	'''

	cr = SuccCallReturn()
	try:
		token = GET(r,'token')
		user = cipher.decryptToken(token)
		if not user:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()
		phone = GET(r,'phone','')
		employee = GET(r,'employee','')
		address = GET(r,'address','')
		addition = GET(r,'addition','')
		term = cm.Terminal.objects.get(id=user['id'])
		term.phone = phone
		term.employee = employee
		term.address = address
		term.addition = addition
		term.save()
	except:
		cr = FailCallReturn()
	return cr.httpResponse()




@csrf_exempt
def getTermVersion(r):
	'''
		获取终端软件最新版本
		读取/svr/audio/setup.cfg
		term_version=0.2.1.0
	'''
	cr = SuccCallReturn()
	try:
		cfg = utils.SimpleConfig()
		cfg.load('/svr/audio/setup.cfg')
		curver =cfg.get('term_version','')
		cr.assign(curver)
	except:
		cr = FailCallReturn()
	return cr.httpResponse()

@csrf_exempt
def getTermInfo(r):
	'''
		更新终端附属信息
	'''

	cr = SuccCallReturn()
	try:
		token = GET(r,'token')
		user = cipher.decryptToken(token)
		if not user:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()
		term = cm.Terminal.objects.get(id=user['id'])
		cr.assign({
			'org':term.org.name,
			'phone':term.phone,
		    'employee':term.employee,
		    'address':term.address,
		    'addition':term.addition
		})
	except:
		cr = FailCallReturn()
	return cr.httpResponse()

@csrf_exempt
def syncPrepare(r):
	cr = SuccCallReturn()
	print 'syncPrepare..'
	try:
		token = GET(r,'token')
		digest = GET(r,'digest')

		if not token or not digest:
			return FailCallReturn(ecode= AppErrors.PARAM_NOT_AVAILABLE).httpResponse()

		user = cipher.decryptToken(token)
		if not user:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()
		if cm.Archive.objects.filter(spx_digest=digest).count():
			cr.assign(0) #0 - 服务器禁止上传 , 文件已上传
#	    		return  FailCallReturn(ecode= AppErrors.FILE_EXISTED).httpResponse()
		else:
			cr.assign(1)
	except:
		#cr = FailCallReturn()
		cr.assign(2)
		traceback.print_exc()
	print 'result:',cr.result
	return cr.httpResponse()

@csrf_exempt
def syncFile_mp3(r):
	'''
		1.接收上传文件mp3
		2.md5 check
		3.读取文件附属信息，写入文件系统和db
		4.录音文件按月份分割到不同目录,根目录从system.conf(store_path)读取
	'''
	import format
	cr = SuccCallReturn()
	print 'syncFile_mp3..'
	try:
		token = GET(r,'token')
		digest = GET(r,'digest')
		content = GET(r,'content')
		if not token or not digest or not content:
			return FailCallReturn(ecode= AppErrors.PARAM_NOT_AVAILABLE).httpResponse()


		term = cipher.decryptToken(token)
		if not term:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()

		content = base64.decodestring(content)
		md5 = utils.getdigest(content)
		if digest!=md5:
			return FailCallReturn(ecode= AppErrors.PARAM_NOT_AVAILABLE,emsg='digest invalid').httpResponse()

		size = len(content)
		if size <= 68: #mp3文件太小
			return FailCallReturn(ecode= AppErrors.DATA_INVALID,emsg='mp3 file corrupted!').httpResponse()

		rs = cm.Terminal.objects.filter(id = term['id'])
		if not rs:
			return FailCallReturn(ecode= AppErrors.OBJECT_NOT_FOUND,emsg='digest invalid').httpResponse()

		terminal = rs[0]
		#文件信息保存在mp3的尾部68字节内
		extra = content[-68:]
		magic,spx_digest,spx_hdr = struct.unpack('!I32s32s',extra)
		if magic !=0xEEAAEEBB:
			return FailCallReturn(ecode= AppErrors.DATA_INVALID,emsg='mp3 file corrupted! magic code dirty!').httpResponse()

		spxinfo = format.parseSpxFileInfoByStream(spx_hdr)
		if not spxinfo:
			return FailCallReturn(ecode= AppErrors.DATA_INVALID,emsg='spx info corrupted!').httpResponse()


		if cm.Archive.objects.filter(digest=spx_digest).count():
			return  FailCallReturn(ecode= AppErrors.FILE_EXISTED).httpResponse()

		t  = cm.Terminal.objects.get(id=term['id'])
		size = len(content)
		storepath = getStorePath(t,size)
		if not os.path.exists(storepath):
			os.makedirs(storepath)

		#创建.attr文件
		filename = spxinfo.filename()+'.attr'
		attrfile =  os.path.join(storepath,filename)
		f = open(attrfile,'w')
		#写入电话终端id，登陆账号
		f.write('%s,%s,%s'%(t.id,t.id,int(time.time())))
		f.close()

		filename = spxinfo.filename()+'.mp3'
		storepath =  os.path.join(storepath,filename)

		f = open(storepath,'wb')
		f.write(content)
		f.close()


		ar = cm.Archive()
		ar.term = t
		ar.digest = md5
		ar.spx_digest = spx_digest
		ar.phone = spxinfo.phone
		ar.name = filename
		ar.path = storepath
		ar.size = len(content)
		ar.rectime = spxinfo.createtime()   #utils.mk_datetime(time.time())
		ar.duration = spxinfo.duration
		ar.uptime = datetime.datetime.now()
		ar.index = spxinfo.index
		ar.attr = spxinfo.attr
		ar.serial = spxinfo.serial
		ar.url=''
		ar.save()
	except:
		cr = FailCallReturn()
		traceback.print_exc()
	print cr.ecode,cr.result
	return cr.httpResponse()


@csrf_exempt
def syncFile(r):
	'''
		1.接收上传spx文件
		2.md5 check
		3.读取文件附属信息，写入文件系统和db
		4.录音文件按月份分割到不同目录,根目录从system.conf(store_path)读取
	'''
	import format
	cr = SuccCallReturn()
	try:
		token = GET(r,'token')
		digest = GET(r,'digest')
		content = GET(r,'content')
		if not token or not digest or not content:
			return FailCallReturn(ecode= AppErrors.PARAM_NOT_AVAILABLE).httpResponse()


		term = cipher.decryptToken(token)
		if not term:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()

		content = base64.decodestring(content)
		md5 = utils.getdigest(content)
		if digest!=md5:
			return FailCallReturn(ecode= AppErrors.PARAM_NOT_AVAILABLE,emsg='digest invalid').httpResponse()

		if cm.Archive.objects.filter(digest=md5).count():
			return  FailCallReturn(ecode= AppErrors.FILE_EXISTED).httpResponse()

		rs = cm.Terminal.objects.filter(id = term['id'])
		if not rs:
			return FailCallReturn(ecode= AppErrors.OBJECT_NOT_FOUND,emsg='digest invalid').httpResponse()

		t = rs[0]

		size = len(content)
		storepath = getStorePath(t,size)
		if not os.path.exists(storepath):
			os.makedirs(storepath)

		spxinfo = format.parseSpxFileInfoByStream(content[:40])
		if not spxinfo:
			return FailCallReturn(ecode= AppErrors.DATA_INVALID,emsg='spx file corrupted!').httpResponse()

		filename = spxinfo.filename()+'.attr'
		attrfile =  os.path.join(storepath,filename)
		f = open(attrfile,'w')
		#写入电话终端id，登陆账号
		f.write('%s,%s,%s'%(t.id,t.id,int(time.time())))
		f.close()

		filename = spxinfo.filename()+'.spx'
		spxfile =  os.path.join(storepath,filename)

		f = open(spxfile,'wb')
		f.write(content)
		f.close()

		ar = cm.Archive()
		ar.term = t
		ar.digest = digest
		ar.spx_digest = digest
		ar.phone = spxinfo.phone
		ar.name = filename
		ar.path = spxfile
		ar.size = len(content)
		ar.rectime = datetime.datetime(spxinfo.year,spxinfo.month,spxinfo.day,spxinfo.hour,spxinfo.minute) #utils.mk_datetime(createtime)
		ar.duration = spxinfo.duration
		ar.uptime = datetime.datetime.now()
		ar.index = spxinfo.index
		ar.attr = spxinfo.attr
		ar.serial = spxinfo.serial
		ar.url=''
		ar.save()

	except:
		cr = FailCallReturn()
		traceback.print_exc()
	return cr.httpResponse()

@csrf_exempt
def getCurrentVersion(r):
	'''
		获取当前终端版本
	'''
	cr = SuccCallReturn()
	try:
		token = GET(r,'token')
		user = cipher.decryptToken(token)
		if not user:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()
		cr.assign(getSysSettings('terminal_version') )
	except:
		cr = FailCallReturn()
	return cr.httpResponse()


@csrf_exempt
def downloadSetupPackage(r):
	'''
		1.gzip压缩
		2.编码base64
	'''
	cr = SuccCallReturn()
	try:
		token = GET(r,'token')
		user = cipher.decryptToken(token)
		if not user:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()

	except:
		cr = FailCallReturn()
	return cr.httpResponse()


@csrf_exempt
def getClientInfoList(r):
	'''
		获取话机相关的客户信息列表
	'''
	cr = SuccCallReturn()
	try:
		token = GET(r,'token')
		user = cipher.decryptToken(token)
		if not user:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()
		term = cm.Terminal.objects.get(id=user['id'])
		cr.assign({
			'org':term.org.name,
			'phone':term.phone,
		    'employee':term.employee,
		    'address':term.address,
		    'addition':term.addition
		})
	except:
		cr = FailCallReturn()
	return cr.httpResponse()



@csrf_exempt
@transaction.commit_manually
def uploadClientInfoList(r):
	'''
		同步本地客户信息到服务器
		[
		{sid,name,....},
		]
	'''
	cr = SuccCallReturn()
	try:
		token = GET(r,'token')
		user = cipher.decryptToken(token)
		if not user:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()
		term = cm.Terminal.objects.get(id=user['id'])
		d = GET(r,'content')
		if not d:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()
		rs = json.loads(d)


#		cm.Client.objects.filter(term__id=user['id']).delete()
		for r in rs:
			c = None				
			recs = cm.Client.objects.filter(term__id=user['id'],sid=r['sid'])
			if recs:
				c = recs[0]
			else:
				c = cm.Client()
				c.term = term
			c.sid = r['sid']
			c.name = r['name']
			c.sex = r['sex']
			c.corp = r['corp']
			c.phone1 = r['phone1']
			c.phone2 = r['phone2']
			c.address= r['address']
			c.postcode=r['postcode']
			c.email = r['email']
			c.website = r['website']
			c.im = r['im']
			c.memo = r['memo']
			c.personid = r['personid']
			c.clientid = r['clientid']
			c.phone3 = r['phone3']
			c.owner_org = r['owner_org']
			c.type = r['type']
			c.pinyin = r['pinyin']
			c.custom_tag = r.get('custom_tag','')
			c.save()
			ars = cm.Archive.objects.filter(client=None,client_sid=c.sid)
			for ar in ars:
				ar.client = c
				ar.save()
		cm.Client.objects.filter(memo='<<DELETE>>').delete()
		
		transaction.commit()
	except:
		transaction.rollback()
		cr = FailCallReturn()
	return cr.httpResponse()


@csrf_exempt
def getClientInfoList(r):
	'''
		从服务器获取客户信息列表
		[
		{sid,name,....},
		]
	'''
	cr = SuccCallReturn()
	try:
		token = GET(r,'token')
		user = cipher.decryptToken(token)
		if not user:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()
		result=[]
		rs = cm.Client.objects.filter(term__id=user['id'])
		for d in rs:
			item={
				'sid':d.sid,
				'name':d.name,
			    'sex':d.sex,
			    'corp':d.corp,
			    'phone1':d.phone1,
			    'phone2':d.phone2,
			    'address':d.address,
			    'postcode':d.postcode,
			    'email':d.email,
			    'website':d.website,
			    'im':d.im,
			    'memo':d.memo,
			    'personid':d.personid,
			    'clientid':d.clientid,
			    'phone3':d.phone3,
			    'owner_org':d.owner_org,
			    'type':d.type,
				'pinyin':d.pinyin,
			    'custom_tag':d.custom_tag
			}
			result.append(item)
		cr.assign(result)
	except:
		cr = FailCallReturn()
	return cr.httpResponse()



# @csrf_exempt
# def updateClientInfo(r):
# 	'''
# 		同步本地客户信息到服务器(单条客户记录)
# 	'''
# 	cr = SuccCallReturn()
# 	try:
# 		token = GET(r,'token')
# 		user = cipher.decryptToken(token)
# 		if not user:
# 			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()
# 		term = cm.Terminal.objects.get(id=user['id'])
# 		cr.assign({
# 			'org':term.org.name,
# 			'phone':term.phone,
# 		    'employee':term.employee,
# 		    'address':term.address,
# 		    'addition':term.addition
# 		})
# 	except:
# 		cr = FailCallReturn()
# 	return cr.httpResponse()

@csrf_exempt
def updateAudioMemo(r):
	'''
		同步本地语音备注信息到服务器
		{
			token,
			spx_digest,
			client_sid,
			memo
		}
	'''
	cr = SuccCallReturn()
	try:
		token = GET(r,'token')
		spxdigest = GET(r,'spx_digest')
		client_sid =GET(r,'client_sid','')
		memo = GET(r,'memo','')
		type = GET(r,'type','')
		productid = GET(r,'productid','')
		operator = GET(r,'operator','')
		user = cipher.decryptToken(token)

		if not user or not spxdigest :
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()
		ar = None
		ars = cm.Archive.objects.filter(spx_digest=spxdigest,term__id=user['id'])
		if ars:
			ar =ars[0]
		c = None
		if client_sid:
			cs = cm.Client.objects.filter(sid=client_sid)
			if cs:
				c = cs[0]
		if ar:
			ar.client =c
			ar.client_sid = client_sid
			ar.memo = memo
			ar.type = type
			ar.productid = productid
			ar.operator = operator

			#print c, 'client_sid:',client_sid,memo,type,productid
			ar.save()
		print 'updateAudioMemo okay'
	except:
		traceback.print_exc()
		cr = FailCallReturn()
	return cr.httpResponse()



@csrf_exempt
def changePwd(r):
	'''
		更新终端 客户经理的登陆密码
		params:  token
				old_pwd
				new_pwd
		status : 0 - succ ; others - errors
	'''
	cr = SuccCallReturn()
	try:

		token = GET(r,'token')
		user = cipher.decryptToken(token)
		if not user:
			return FailCallReturn(ecode= AppErrors.UNAUTHORIZED).httpResponse()
		oldpwd = GET(r,'old_pwd')
		newpwd = GET(r,'new_pwd')
		print oldpwd,newpwd
		if not oldpwd or not newpwd:
			return FailCallReturn(ecode= AppErrors.PARAM_NOT_AVAILABLE).httpResponse()

		term = cm.Terminal.objects.get(id=user['id'])
		if term.passwd!=oldpwd:
			return FailCallReturn(ecode= AppErrors.PASSWD_INVALID).httpResponse()
		if len(newpwd) > 20:
			return FailCallReturn(ecode= AppErrors.DATA_INVALID).httpResponse()
		term.passwd = newpwd
		term.save()
	except:
		cr = FailCallReturn()
	return cr.httpResponse()

