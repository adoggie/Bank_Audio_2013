# -*- coding: utf-8 -*-

#filesync.py
#扫描语音文件目录 $app/upload
#上传文件到webserver
#将文件从$app/upload 移动到 $app/录音文件 目录

from base import *
import utils

import os,sys,os.path,traceback,logging,time,struct,pickle,datetime,json,base64
import urllib
from dbconn import *
import convert
import format
import inspect

def prepare(digest):
	'''
		准备发送到服务器
		@return:
			0 - 服务器禁止上传 , 文件已上传
			1 - 服务器允许接收
			2 - 处理异常
	'''
	params = urllib.urlencode({'token':getApp().getToken(),'digest':digest})
	#print r[2]
	version=''
	try:
		server = getApp().getSettings().get('webserver')
		if server.find('http')==-1:
			server = 'http://'+server
		f = urllib.urlopen('%s/WebApi/Terminal/syncPrepare'%(server),params)   # POST
		d = f.read()
		print 'server return:',d
		d = json.loads(d)
		if d['status'] == 0:
			return d['result']
	except:
		traceback.print_exc()

	return 2

def syncFile_mp3(mp3file):
	'''
		将文件转换成base64
	'''

	try:
		print 'do syncFile:',mp3file
		digest = utils.getfiledigest(mp3file)
#		return prepare(digest)

		f = open(mp3file,'rb')
		c = f.read()
		f.close()
		s = base64.encodestring(c).strip()
		params = urllib.urlencode({'token':getApp().getToken(),'digest':digest,'content':s})
		print 'file len:',len(s)

		server = getApp().getSettings().get('webserver')
		if server.find('http')==-1:
			server = 'http://'+server
		f = urllib.urlopen('%s/WebApi/Terminal/syncFile'%(server),params)   # POST
		d = f.read()
		print 'sync file returns:',d
		d = json.loads(d)

		if d['status'] == 0 :
			return True
	except:
		traceback.print_exc()
	return False


def syncFile(spxfile,digest=''):
	'''
		将文件转换成base64
	'''

	try:
		print 'do syncFile:',spxfile
#		digest = utils.getfiledigest(mp3file)

		f = open(spxfile,'rb')
		c = f.read()
		f.close()
		s = base64.encodestring(c).strip()
		params = urllib.urlencode({'token':getApp().getToken(),'digest':digest,'content':s})
		print 'file len:',len(s)

		server = getApp().getSettings().get('webserver')
		if server.find('http')==-1:
			server = 'http://'+server
		f = urllib.urlopen('%s/WebApi/Terminal/syncFile'%(server),params)   # POST
		d = f.read()
		print 'sync file returns:',d
		d = json.loads(d)

		if d['status'] == 0 :
			return True
	except:
		traceback.print_exc()
	return False


def scan():
	'''
		扫描文件，写入db，再进行文件传输
	'''
	import dbsql
	path = getApp().getAudioStorePath()
	db = getApp().getDB()
	#扫描文件目录，找出差异文件，并写入db
	print 'scan :',path
	for root, dirs, files in os.walk(path):
		for file in files:
			time.sleep(0.001)
			if not getApp().running:
				return

			file = file.strip().lower()
			if file.find('.spx') == -1:
				continue
			spxfile = root+'/'+file
			try:
#				print 'ready for ',spxfile
				if  db.getRecCountBySpxFile(spxfile):
#					print 'file  has registered in db!'
					continue  #已处理
				spx_digest = utils.getfiledigest(spxfile)
				if db.getRecCountByDigest(spx_digest):
#					print 'has upload by digest!'
					continue #已处理
				db.appendSpxFile(spxfile,spx_digest,0) #未上传
			except:
				traceback.print_exc()

def sync_mp3():

	db = getApp().getDB()
	#从db中取出未上传部分，执行文件同步
	sql = 'select * from core_audiofile where status= 0 '
	cr = db.handle().cursor()
	cr.execute(sql)
	rs = fetchallDict(cr)
	cr = None
	for r in rs:
		spxfile,digest = r['spxfile'],r['digest']
		try:
			if not getApp().running:
				return
			spxfile = spxfile.decode('utf-8')
			if not spxfile or not os.path.exists(spxfile):
				sql = 'delete from core_audiofile where digest=?'
				cr = db.handle().cursor()
				cr.execute(sql,(digest,))
				db.handle().commit()
				continue
			print __file__,inspect.currentframe().f_lineno, spxfile
			rc = prepare(digest)
			print 'prepare result:',rc
			if rc not in (0,1): # 2
				getApp().token = ''
				return              #网络访问异常，返回，等待下次再次执行sync
			if rc ==1: #开始同步文件到服务器
				#读文件 失败 可能文件未写完，要求话机上传程序写入文件时，独占写入
				mp3file =''
				try:
					mp3file = convert.spx_convert_mp3(spxfile,'')
				except:
					traceback.print_exc()
				if not mp3file: #文件转换失败，更名  处理失败，删除数据库记录
					#print spxfile,spxfile.replace('.spx','._spx')
					if os.path.exists(spxfile):
						os.rename(spxfile,spxfile.replace('.spx','._spx'))
					sql = 'delete from core_audiofile where digest=?'
					cr = db.handle().cursor()
					cr.execute(sql,(digest,))
					db.handle().commit()
					continue
				digest = utils.getfiledigest(mp3file)
				if not digest:
					continue
				if not syncFile_mp3(mp3file):
					print 'syncFile failed!'
					getApp().token = ''
					return
			#上传okay ，标识文件已经被上传了
			sql = 'update core_audiofile set status=1 ,uptime=? where digest=?'
			cr = db.handle().cursor()
			cr.execute(sql,(int(time.time()),digest))
			db.handle().commit()
		except:
			traceback.print_exc()

def sync():
	db = getApp().getDB()
	#从db中取出未上传部分，执行文件同步
	sql = 'select * from core_audiofile where status= 0 '
	cr = db.handle().cursor()
	cr.execute(sql)
	rs = fetchallDict(cr)
	cr = None
	for r in rs:
		spxfile,digest = r['spxfile'],r['digest']
		try:
			if not getApp().running:
				return
			spxfile = spxfile.decode('utf-8')
			if not spxfile or not os.path.exists(spxfile):
				sql = 'delete from core_audiofile where digest=?'
				cr = db.handle().cursor()
				cr.execute(sql,(digest,))
				db.handle().commit()
				continue
			print __file__,inspect.currentframe().f_lineno, spxfile
			rc = prepare(digest)
			print 'prepare result:',rc
			if rc not in (0,1): # 2
				getApp().token = ''
				return              #网络访问异常，返回，等待下次再次执行sync
			if rc ==1:              #开始同步文件到服务器
									#读文件 失败 可能文件未写完，要求话机上传程序写入文件时，独占写入
				if not syncFile(spxfile,digest):
					print 'syncFile failed!'
					#continue
					getApp().token = ''
					return  #此时可能当前login用户在服务器上已经被删除,导致同步失败
			#上传okay ，标识文件已经被上传了
			sql = 'update core_audiofile set status=1 ,uptime=? where digest=?'
			cr = db.handle().cursor()
			cr.execute(sql,(int(time.time()),digest))
			db.handle().commit()
		except:
			traceback.print_exc()

def test_walk():
	cnt = 0
	start=time.time()
	for root, dirs, files in os.walk('c:/windows'):
		time.sleep(0.001)
		cnt+=len(files)
	end = time.time()
	print 'cost seconds:',(end-start)
	print 'file scaned:',cnt

if __name__ == '__main__':
#	test_walk()

	getApp().token="HNAh/KiOPhVR+Ikz9gpZanjokzfwG5wft/0I9clwOPBRVjfbWELuYjtdZpH8UrM1lz2oVCuSmM4J\ndEQwS6WcHFR/0oKljgWLyrLCtar2jtcGwy3VixfmYBfuHHMn9Nq22gs5dLTE7ukN2PNUJPu4UklG\nCgAr/8A1WfntmbYKhd/f+1eHJ4l3yfoBnkc5iSzNaF1akkwkOj83OhzWNlSQynlOO/T4JMQqYenm\nA0xgGFX49EvdSJdEWw=="
	filepath = convert.spx_convert_mp3('c:\\201104240855_000920_xxxxxxxxxxxx31198606.spx')
	print syncFile(filepath)


