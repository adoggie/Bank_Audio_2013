# -*- coding: utf-8 -*-

#upgrade.py
#软件版本更新
#从服务器获取当前终端软件版本
#下载到本地upgrade目录,待再次运行adloader执行安装

from base import *

import os,sys,os.path,traceback,logging,time,struct,pickle,datetime,json,base64
import urllib

def getCurrentVersion():
	params = urllib.urlencode({'token':getApp().getToken()})
	#print r[2]
	version=''
	try:
		server = getApp().getSettings().get('webserver')
		if server.find('http')==-1:
			server = 'http://'+server
		f = urllib.urlopen('%s/WebApi/Terminal/getCurrentVersion'%(server),params)   # POST
		d = f.read()

		d = json.loads(d)
		if d['status'] == 0:
			version = d['result']['version']
	except:
		traceback.print_exc()
	return version


def downloadSetupPackage(version):
	'''
		下载指定版本的终端软件安装包
		存放到$app/temp/
		result:{digest,file,gzip(content)}
	'''
	r = False
	params = urllib.urlencode({'token':getApp().getToken(),'version':version})
	try:
		server = getApp().getSettings().get('webserver')
		if server.find('http')==-1:
			server = 'http://'+server
		f = urllib.urlopen('%s/WebApi/Terminal/downloadSetupPackage'%(server),params)   # POST
		d = f.read()
		d = json.loads(d)
		if d['status'] != 0:
			return False
		media = d['result']
		md5 = media['digest']
		file = media['file']        #filename
		c = media['content']
		c = base64.decodestring(c)
		#-- ungzip
		import StringIO
		import gzip
		import utils
		digest = utils.getdigest(c)
		if digest!=md5:
			print 'upgrade package md5 check failed!'
			return False

		compressedstream = StringIO.StringIO(c)
		gzipper = gzip.GzipFile(fileobj=compressedstream)
		c = gzipper.read()
		#-- write  file
		path = getApp().getTempPath()
		f = open(path+'/'+file,'wb')
		f.write(c)
		f.close()
		r = True
	except:
		traceback.print_exc()
	return r


def checkVersion():
	'''
	检查软件版本
	0 - no new software ver
	1 - download software okay
	2 - download failed
	'''

	ver = getApp().getSettings().get('version')
	ver_server = getCurrentVersion()
	if ver == ver_server:
		return 0
	r = downloadSetupPackage(ver_server)
	if r:
		return 1
	return 2

