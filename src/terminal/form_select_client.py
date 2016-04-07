# -*- coding: utf-8 -*-


from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,time,datetime,traceback,string,json,pickle,os,os.path
from  ui_client_select import *
import utils
from base import *
import dbsql
from dbconn import *




class FormSelectClient(QtGui.QFrame,Ui_FrameClientSelect):
	handle = None

	def __init__(self,parent=None):
		QtGui.QFrame.__init__(self,parent)
		self.setupUi(self)
		self.db = dbsql.SqlPrepare()
		self.connect(self.btnQuery,SIGNAL('clicked()'),self.onDoQuery)
		self.connect(self.btnThatIs,SIGNAL('clicked()'),self.onSelect)

#		self.show()



		self.tvClients.setHeaderLabels([
			u'序号',
		    u'客户名称',
		    u'性别',
		    u'公司',
		    u'电话1',
			u'电话2',
			u'电话3',
		    u'地址',
		    u'',
		])

		self.tvClients.resizeColumnToContents(0)
		self.connect(self.tvClients,SIGNAL('itemDoubleClicked(QTreeWidgetItem*,int)'),self.onTreeItemDblClick_Clients)
#		self.connect(self.tvClientList,SIGNAL('itemClicked(QTreeWidgetItem*,int)'),self.onTreeItemClick_Clients)
		self.idxdata={}
		self.tvClients.setAlternatingRowColors(True)

		font = QtGui.QFont(AppConst.APP_FONT_NAME,10)
		self.setFont(font)




	@staticmethod
	def instance(parent=None):
		if not FormSelectClient.handle:
			FormSelectClient.handle = FormSelectClient(parent)
		return FormSelectClient.handle


	def onTreeItemDblClick_Clients(self,ti,col):
		self.onSelect()

	def onDoQuery(self):
		self.idxdata={}
		self.tvClients.clear()
		text = self.edtContent.text().toUtf8().data().strip()
		sql = "select * from core_client where 1=1 and memo !='%s'"%AppConst.CLIENT_DELETED_MARKER
		if text:
			sql +=" and (name like '%%%s%%' or clientid like '%%%s%%' ) "%(text,text)
		sql+= " order by pinyin "
#		print sql
		cr = self.db.handle().cursor()
		cr.execute(sql)
		rs = fetchallDict(cr)
		idx = 0
		for r in rs:
			idx+=1
			sex = u'男'
			if int(r['sex'])!=1:
				sex = u'女'

			row = (str(idx),
					r['name'].decode('utf-8'),
					sex,
			        r['corp'].decode('utf-8'),
			        r['phone1'].decode('utf-8'),
			        r['phone2'].decode('utf-8'),
			        r['phone3'].decode('utf-8'),
			        r['address'].decode('utf-8')
				)
			ti = QTreeWidgetItem(row )
			self.tvClients.addTopLevelItem(ti)
			self.idxdata[ti] = (r['sid'],r['name'])

	def select(self,cbData):
		self.show()
		self.cbRecv = cbData
		self.onDoQuery()


	def onSelect(self):
#		tis = self.tvClients.selectedItems()
#		if not tis:
#			return
#		ti = tis[0]
		ti = self.tvClients.currentItem()
		if not ti:
			return

		sid,name =self.idxdata[ti]
		self.cbRecv(sid,name) #返回选择客户信息到用户
		self.hide()


	def closeEvent(self,event):
		#FormSelectClient.handle = None
		self.hide()
		event.ignore()




	def showNote(self,note):
		'''
			note: {
				spx_digest,
				spx_index,  录音文件索引号
			}
		'''
		self.note = note
		cr = self.db.handle().cursor()
		sql=''
		digest = note.get('spx_digest')
		index = note.get('spx_index')
		if digest:

			sql = 'select * from core_audiofile where digest=?'
			cr.execute(sql,(digest,))
			rs = fetchallDict(cr)
			if rs:
				r = rs[0]
				self.edtPhone.setText(r['phone'].decode('utf-8'))
				attr = u'未知'
				if r['attr'] == 0 :
					attr=u'来电'
				elif r['attr'] == 1:
					attr=u'去电'
				elif r['attr'] == 2:
					attr=u'录音'
				elif r['attr'] == 3:
					attr = u'未接'
				self.edtToneAttr.setText(attr)
				self.edtToneTime.setText(utils.formatTimeLength(r['duration']))
				self.edtToneMemo.setText(r['memo'].decode('utf-8'))
				sid = r['client_sid']

				if sid:
					sql = 'select * from core_client where sid=?'
					cr.execute(sql,(sid,))
					rs = fetchallDict(cr)
					if rs:
						name = rs[0]['name']
						self.edtClientName.setText(name.decode('utf-8'))



if __name__=='__main__':
	pass