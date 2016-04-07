# -*- coding: utf-8 -*-

#archive.py
#录音资料同步


import os,sys,os.path,traceback,logging,time,struct,pickle,datetime,json,base64
import urllib

import utils
from base import *
from dbconn import *
import dbsql

#将录音文件memo_status为0的记录上传到服务器
def syncToServer(db):
	'''
		将本地录音信息同步到服务器
	'''
	try:
		cr = db.cursor()
		#保证 录音文件mp3已经被上传到服务器了
		sql = 'select * from core_audiofile where status=1 and memo_status=0'
		cr.execute(sql)
		rs = fetchallDict(cr)
		set=[]
		for r in rs:
			if not getApp().running:
				return
			digest = r['digest']
			client_sid = r['client_sid']
			memo = r['memo']
			type = r['type']
			productid=r['productid']
			operator = utils.normalizeString(r['operator'])

			#一次发送每条需要更新的录音记录信息
			params = urllib.urlencode({'token':getApp().getToken(),
			                           'spx_digest':digest,
			                           'client_sid':client_sid,
			                           'memo':memo,
			                           'type':type,
			                           'productid':productid,
			                           'operator':operator
									})
			server = getApp().getSettings().get('webserver')
			if server.find('http')==-1:
				server = 'http://'+server
			f = urllib.urlopen('%s/WebApi/Terminal/updateAudioMemo'%(server),params)   # POST
			d = f.read()
			print d
			d = json.loads(d)
			if d['status'] != 0 :
				return False
			sql = 'update core_audiofile set memo_status=1 where digest=?'
			cr.execute(sql,(digest,))
			db.commit()
			print 'archive (digest: %s) has been update to server!'%(digest)
		return True
	except:
		traceback.print_exc()
	return False

if __name__ == '__main__':
	pass
#	items = import_from_xls(r'c:/aaaa.xls')
#	print items



