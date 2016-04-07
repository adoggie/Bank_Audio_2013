# -*- coding: utf-8 -*-


from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,time,datetime,traceback,string,json,pickle,os,os.path
from  ui_dial import *
import utils
from base import *
import dbsql
from dbconn import *

import usbcmd


class FormDial(QtGui.QFrame,Ui_FrameDial):
	handle = None
	def __init__(self,parent=None):
		QtGui.QFrame.__init__(self,parent)
		self.setupUi(self)
		self.db = dbsql.SqlPrepare()
		self.connect(self.btnDial,SIGNAL('clicked()'),self.onBtnDialClick)
		self.connect(self.cbxClients,SIGNAL('currentIndexChanged(int)'),self.onClientIndexChanged)
		self.connect(self.cbxPhoneNum,SIGNAL('editTextChanged(const QString&)'),self.onEditPhoneChanged)



		self.setWindowTitle(u'电话拨号')
		self.raise_()
		self.clients={}
		self.reflect = 0
		self.reflect2 = 0

		self.setWindowFlags( Qt.Dialog )
		self.show()
		self.cbxPhoneNum.setCompleter(None)


	@staticmethod
	def instance(parent=None):
		if not FormDial.handle:
			FormDial.handle = FormDial(parent)
		return FormDial.handle

	def onEditPhoneChanged(self,text):
		'''
			输入电话，显示客户名称
		'''
		if self.reflect2 == 1:
			return

		# self.cbxClients.setCurrentIndex(-1)
		phone = text.toUtf8().data().strip()
		if not phone:
			return

		phone = self.cbxPhoneNum.currentText()
		csid = ''
		for n in range(self.cbxPhoneNum.count()):
			name = self.cbxPhoneNum.itemText(n)
			if phone == name:
				csid = self.cbxPhoneNum.itemData(n).toString().toUtf8().data()
		phone = phone.toUtf8().data().strip()
		if not csid:
			cr = self.db.handle().cursor()
			sql = "select * from core_client where memo!='%s' and (phone1=? or phone2=? or phone3=?)" %AppConst\
				.CLIENT_DELETED_MARKER
			cr.execute(sql,(phone,phone,phone))
			rs = fetchallDict(cr)
			print 'you input:',text
			if not rs:
				self.reflect = 1
				self.cbxClients.setCurrentIndex(-1)
				self.reflect = 0
				return
			r = rs[0]
			csid = r['sid']
		print csid
		idx = self.cbxClients.findData(csid)
		if idx == -1:
			return
		self.reflect = 1
		self.cbxClients.setCurrentIndex(idx)
		# if self.cbxClients.currentIndex()!=idx:
		# 	self.cbxClients.setCurrentIndex(idx)
		# else:
		# 	self.cbxClients.setCurrentIndex(-1)
		self.reflect = 0


	def onClientIndexChanged(self,index):
		print 'client list index changed..'
		if self.reflect == 1:
			return
		if index == -1:
			return
		csid = self.cbxClients.itemData(index).toString().toUtf8().data()
		self.cbxPhoneNum.clear()
		r = self.clients.get(csid)

		if not r:
			return
		self.reflect2 = 1
		if r['phone1']:
			self.cbxPhoneNum.addItem(r['phone1'],csid)
		if r['phone2']:
			self.cbxPhoneNum.addItem(r['phone2'],csid)
		if r['phone3']:
			self.cbxPhoneNum.addItem(r['phone3'],csid)

		self.cbxPhoneNum.setCurrentIndex(0)
		self.reflect2 = 0

	def onBtnDialClick(self):
		phone = self.cbxPhoneNum.currentText().toUtf8().data().strip()
		if not phone:
			QMessageBox.about(self,u'提示',u'请输入电话号码!')
			return
		#执行拨号
		usbcmd.UsbHost.instance().phoneDial(phone)
		import form_tone_ring
		csid=''
		if self.cbxClients.currentIndex()!=-1:
			csid = self.cbxClients.itemData(self.cbxClients.currentIndex()).toString().toUtf8().data()

		form_tone_ring.FormToneRing.instance().showOutgoingCall(phone,csid)

		import form_audio_note
		form_audio_note.currrent_dial_out_csid = csid
		self.close()



	def showPhoneNum(self,client_sid):
		cr = self.db.handle().cursor()
		sql = "select * from core_client where memo!='%s' order by pinyin"%AppConst.CLIENT_DELETED_MARKER
		cr.execute(sql)
		rs = fetchallDict(cr)
		idx = 0
		for r in rs:
			self.clients[r['sid']] = r
			self.cbxClients.addItem(r['name'].decode('utf-8'),r['sid'])
			if client_sid == r['sid']:
				self.reflect2 = 1
				self.cbxClients.setCurrentIndex(idx)
				self.reflect2 = 0
			idx+=1
		self.raise_()

	def showPhoneNum2(self,phone):


		cr = self.db.handle().cursor()
		sql = "select * from core_client where memo!='%s' order by pinyin"%AppConst.CLIENT_DELETED_MARKER
		cr.execute(sql)
		rs = fetchallDict(cr)
		idx = 0
		for r in rs:
			self.clients[r['sid']] = r
			self.cbxClients.addItem(r['name'].decode('utf-8'),r['sid'])
			idx+=1

#		self.cbxPhoneNum.addItem(phone)
#		self.cbxPhoneNum.setCurrentIndex(0)
		self.cbxClients.setCurrentIndex(-1)
		self.cbxPhoneNum.setEditText(phone)


		self.raise_()


	def closeEvent(self, event ):
		FormDial.handle = None

if __name__=='__main__':
	pass