# -*- coding: utf-8 -*-

#client.py



import os,sys,os.path,traceback,logging,time,struct,pickle,datetime,json,base64
import urllib

import xlrd
import utils
from base import *
from dbconn import *
import dbsql


#客户名称 性别 公司 电话1 电话2 地址 邮编 邮件 网站地址 qq/msn 备注'

def export_to_xls(file,db):
	import xlwt
	hdr=u'客户名称 身份证编号 客户ID 性别 公司 电话1 电话2 地址 邮编 邮件 网站地址 qq/msn 备注'
	hdr=u'客户名称 身份证编号 客户ID 性别 公司 电话1 电话2 电话3 地址 邮编 邮件 客户类别 归属机构 备注 自定义标签'
	try:
		wbk = xlwt.Workbook()
		sheet = wbk.add_sheet('sheet 1')
		#写表头
		fs = hdr.split(u' ')
		c = 0
		for f in fs:
			sheet.write( 0,c,f)
			c+=1
		r = 1
		print 'do export client-list..'
		cr = db.cursor()
		sql = 'select * from core_client where memo!=? order by pinyin'
		cr.execute(sql,(AppConst.CLIENT_DELETED_MARKER,))
		rs = fetchallDict(cr)
		for d in rs:
			if d['sex']:
				d['sex'] = '男'
			else:
				d['sex'] ='女'
			values=[
				d['name'],
			    d['personid'],
			    d['clientid'],
				d['sex'],
				d['corp'],
				d['phone1'],
				d['phone2'],
				d['phone3'],
				d['address'],
				d['postcode'],

				d['email'],
			    AppConst.getClientTypeName(d['type']).encode('utf-8'),
			    d['owner_org'],
#				d['website'],
#				d['im'],
				d['memo'],
				d['custom_tag']
			]

			values=map(str,values)
			values=map(lambda  x: x.decode('utf-8'),values)
			#				print values
			for c in range(len(values)):
				sheet.write(r,c,values[c] )
			r+=1
		wbk.save(file)
		return True
	except:
		traceback.print_exc()
		return False


def import_from_xls(xlsfile,db):
	'''
		@return:
			[ [name,sex,corp,phone1,....],..]
	'''


	try:
		book = xlrd.open_workbook(xlsfile)
		sheet = book.sheet_by_index(0)
		row = 0
		if sheet.cell_value(0,0)==u'客户名称':
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
				elif type(values[n]) == type(0.1):
					values[n] = int(values[n])
				else:
					values[n] = str(values[n])
			item={
				'name':values[0],
			    'personid': values[1],
			    'clientid': values[2],
			    'sex':values[3],
			    'corp':values[4],
			    'phone1':values[5],
			    'phone2':values[6],
			    'phone3':values[7],

			    'address':values[8],
			    'postcode':values[9],
			    'email':values[10],
			    'type': values[11],  #客户类别
			    'owner_org':values[12], #归属机构
			    'memo':values[13],
			    'custom_tag':''
			}
			if len(values)>14:
				item['custom_tag']=values[14]

			#item['sex'] = 1
			# for k,v in item.items():
			# 	print k,type(v)
			# 	if type(v) == type(0.1):
			# 		item[k] = int(item[k])
			try:

				item['type'] = AppConst.getClientTypeId(item['type'].decode('utf-8'))
				#item['type'] = int(item['type'])
			except:
				item['type'] = 0

			result.append(item)
		#-------------------------------------------------
		# update into database
		cr = db.cursor()
		for r in result:

			sql = "select * from core_client where name=? and memo!='%s'"%AppConst.CLIENT_DELETED_MARKER
			cr.execute(sql,(r['name'],))
			rs2 = fetchallDict(cr)
			#写入记录
			pinyin = utils.multi_get_letter(r['name'])
			if r['sex']=='男':
				r['sex'] = 1
			else:
				r['sex'] = 0
			sid = ''
			insert = True
			if rs2:
				insert = False
				sid = rs2[0]['sid']

			if not insert:
				sql = "update core_client set name=?,sex=?,corp=?,phone1=?,phone2=?,address=?,postcode=?," \
				      "email=?,website=?,im=?,memo=?,personid=?,clientid=?,pinyin=?,status=?,phone3=?," \
				      "owner_org=?,type=?,custom_tag=?    where sid=?"
				cr.execute(sql,(
					r['name'],r['sex'],r['corp'],
					r['phone1'],r['phone2'],
					r['address'],
				    r['postcode'],r['email'],
				    '',#r['website'],
				    '',#r['im'],
				    r['memo'],
				    r['personid'],
				    r['clientid'],
				    pinyin,
				    0,   # status is unuploaded
					r['phone3'],
				    r['owner_org'],
				    r['type'],
					r['custom_tag'], #2013.11.8
				    sid
				))

			else: # new one , insert
				sql = "insert into core_client values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
				sid = dbsql.gen_sid()

				cr.execute(sql,(
					sid,
					r['name'],r['sex'],r['corp'],
					r['phone1'],r['phone2'],
					r['address'],
				    r['postcode'],r['email'],
				    '',#r['website'],
				    '',#r['im'],
				    r['memo'],
				    r['personid'],
				    r['clientid'],
				    pinyin,
				    0,   # status is unuploaded
					r['phone3'],
				    r['owner_org'],
				    r['type'],
				    r['custom_tag']

				))
				#匹配到电话记录
				#-- 将phone1，phone2匹配到录音记录上去
				phone1 = r['phone1']
				phone2 = r['phone2']
				phone3 = r['phone3']
				if not phone1: phone1= 'z-'*100
				if not phone2: phone2 = 'z-'*100
				if not phone3: phone3 = 'z-'*100
				sql = 'update core_audiofile set client_sid=?,memo_status=0 ' \
				      'where (phone=? or phone=? or phone=?) and client_sid=? and attr!=2'
				cr.execute(sql,(sid,phone1,phone2,phone3,'') )

		db.commit()
	except:
		traceback.print_exc()
		db.rollback()
		return False
	return True



def syncToServer(db):
	'''
		将本地客户资料同步到服务器
	'''
	try:
		cr = db.cursor()
		sql = 'select * from core_client where status=0 order by pinyin'
		cr.execute(sql)
		rs = fetchallDict(cr)
		set=[]
		for d in rs:

			item={
				'sid':d['sid'],
				'name':d['name'],
			    'sex':d['sex'],
			    'corp':d['corp'],
			    'phone1':d['phone1'],
			    'phone2':d['phone2'],
			    'address':d['address'],
			    'postcode':d['postcode'],
			    'email':d['email'],
			    'website':d['website'],
			    'im':d['im'],
			    'memo':d['memo'],
			    'personid':d['personid'],
			    'clientid':d['clientid'],
			    'phone3':d['phone3'],
			    'owner_org':d['owner_org'],
			    'type':d['type'],
				'pinyin':d['pinyin'],
			    'custom_tag':d['custom_tag']
			}
			set.append(item)

		if not set:
			return True

		d = json.dumps(set)
		params = urllib.urlencode({'token':getApp().getToken(),'content':d})


		server = getApp().getSettings().get('webserver')
		if server.find('http')==-1:
			server = 'http://'+server
		f = urllib.urlopen('%s/WebApi/Terminal/uploadClientInfoList'%(server),params)   # POST
		d = f.read()
		print 'sync clients returns:',d
		d = json.loads(d)
		if d['status'] != 0 :
			return False
#		print rs
		for r in rs:
			sql = 'update core_client set status=1 where sid=?'
			print sql ,r['sid']
			cr.execute(sql,(r['sid'],) )
			sql ="delete from core_client where memo='<<DELETE>>'"
			cr.execute(sql)
		db.commit()
	except:
		traceback.print_exc()
		return False
	return True


def syncFromServer(db):
	'''
		从服务器同步客户资料到本地数据库
		如果本地存在，则不做处理，不存在则增加
	'''
	try:
		params = urllib.urlencode({'token':getApp().getToken()})
		server = getApp().getSettings().get('webserver')
		if server.find('http')==-1:
			server = 'http://'+server
		f = urllib.urlopen('%s/WebApi/Terminal/getClientInfoList'%(server),params)   # POST
		d = f.read()
		d = json.loads(d)

		if d['status'] != 0 :
			return False
		rs =d['result']

		cr = db.cursor()
		for r in rs:
			sql = 'select count(*) as cnt from core_client where sid=?'
			cr.execute(sql,(r['sid'],))
			cnt = fetchoneDict(cr)['cnt']
			if int(cnt):    #客户信息存在 ,pass
				continue
			#写入记录
			sql = "insert into core_client values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
			#sid = dbsql.gen_sid()
			sid = r['sid']
			cr.execute(sql,(
				sid,
				r['name'],r['sex'],r['corp'],
				r['phone1'],r['phone2'],r['address'],
			    r['postcode'],r['email'],
			    '',#r['website'],
			    '',#r['im'],
			    r['memo'],
			    r['personid'],
			    r['clientid'],
			    r['pinyin'],
			    #r['status'],
				1,
			    r['phone3'],
			    r['owner_org'],
			    r['type'],
			    r['custom_tag']
			))
		db.commit()
		return True
	except:
		traceback.print_exc()
	return False

if __name__ == '__main__':
	items = import_from_xls(r'c:/aaaa.xls')
	print items



