# -*- coding: utf-8 -*-


from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ctypes
from ctypes import *

import sys,threading,time,datetime,traceback,string,json,pickle,os,os.path
from  ui_client_info import *
import utils
from base import *
import message
import dbsql
from dbconn import *




class FormClientInfo(QtGui.QFrame,Ui_FrameClientInfo):
	handle = None

	def __init__(self,parent=None):
		QtGui.QFrame.__init__(self,parent)
		self.setupUi(self)
		self.db = dbsql.SqlPrepare()
		self.connect(self.btnSave,SIGNAL('clicked()'),self.onBtnSaveClick)
		self.cbxSex.addItem(u'女',0)
		self.cbxSex.addItem(u'男',1)

		for k,v in AppConst.CLIENT_TYPES:
			self.cbxType.addItem(v,k)

		self.setWindowFlags( Qt.Dialog )
		self.show()
		self.cur_sid = ''
		self.raise_()

		font = QtGui.QFont(AppConst.APP_FONT_NAME,10)
		self.setFont(font)

	@staticmethod
	def instance(parent=None):
		if not FormClientInfo.handle:
			FormClientInfo.handle = FormClientInfo(parent)
		return FormClientInfo.handle

	def onBtnSaveClick(self):
		phone1 = self.edtPhone1.text().toUtf8().data().strip()
		phone2 = self.edtPhone2.text().toUtf8().data().strip()
		phone3 = self.edtPhone3.text().toUtf8().data().strip()

		name = self.edtName.text().toUtf8().data().strip()
		pinyin = utils.multi_get_letter(name)
		if self.cur_sid:
			sql = "update core_client set name=?,sex=?," \
			      "corp=?,phone1=?,phone2=?,address=?,postcode=?,email=?," \
			      "memo=?,personid=?,clientid=?,pinyin=?,status=0,phone3=?,owner_org=?,type=?,custom_tag=? where sid=?"

			if not name:
				QMessageBox.about(self,u'提示',u'名称不能为空!')
				return
			try:
				cr = self.db.handle().cursor()
				cr.execute(sql,(
					name,
					self.cbxSex.itemData(self.cbxSex.currentIndex()).toInt()[0],
				    self.edtCorp.text().toUtf8().data().strip(),
				    self.edtPhone1.text().toUtf8().data().strip(),
				    self.edtPhone2.text().toUtf8().data().strip(),
				    self.edtAddress.text().toUtf8().data().strip(),
				    self.edtPostCode.text().toUtf8().data().strip(),
				    self.edtMail.text().toUtf8().data().strip(),

#				    self.edtWebSite.text().toUtf8().data().strip(),
#				    self.edtIm.text().toUtf8().data().strip(),
				    self.edtMemo.toPlainText().toUtf8().data().strip(),
					self.edtPersonId.text().toUtf8().data().strip(),
					self.edtClientId.text().toUtf8().data().strip(),
					pinyin,
					self.edtPhone3.text().toUtf8().data().strip(),
					self.edtOwnerOrg.text().toUtf8().data().strip(),
					self.cbxType.currentIndex(),
					self.edtCustomTag.text().toUtf8().data().strip(),
				    self.cur_sid
				))
				self.db.handle().commit()
			except:
				traceback.print_exc()
				QMessageBox.about(self,u'提示',u'数据输入不合法!')
				return
		else:
#			name = self.edtName.text().toUtf8().data().strip()
			if not name:
				QMessageBox.about(self,u'提示',u'名称不能为空!')
				return
			#check if  same name existed
			sql = "select count(*) as cnt from core_client where name=?"
			cr = self.db.handle().cursor()
			cr.execute(sql,(name,))
			r = fetchoneDict(cr)
			if r['cnt']:
				QMessageBox.about(self,u'提示',u'重复的客户名称!')
				return
			#-------------------------------------------------------
			sql = "insert into core_client values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"

			try:
				sid = dbsql.gen_sid()
				cr = self.db.handle().cursor()
				cr.execute(sql,(
					 sid,
					name,
					self.cbxSex.itemData(self.cbxSex.currentIndex()).toInt()[0],
					self.edtCorp.text().toUtf8().data().strip(),
					self.edtPhone1.text().toUtf8().data().strip(),
					self.edtPhone2.text().toUtf8().data().strip(),
					self.edtAddress.text().toUtf8().data().strip(),
					self.edtPostCode.text().toUtf8().data().strip(),
					self.edtMail.text().toUtf8().data().strip(),
					'', #website
					'', #im
#					self.edtWebSite.text().toUtf8().data().strip(),
#					self.edtIm.text().toUtf8().data().strip(),
					self.edtMemo.toPlainText().toUtf8().data().strip(),
					self.edtPersonId.text().toUtf8().data().strip(),
					self.edtClientId.text().toUtf8().data().strip(),
					pinyin,
					0,
					self.edtPhone3.text().toUtf8().data().strip(),
					self.edtOwnerOrg.text().toUtf8().data().strip(),
					self.cbxType.currentIndex(),
					self.edtCustomTag.text().toUtf8().data().strip()
				))
				self.db.handle().commit()
				self.cur_sid = sid
			except:
				traceback.print_exc()
				QMessageBox.about(self,u'提示',u'数据输入不合法!')
				return

		if not phone1: phone1= 'z-'*100
		if not phone2: phone2 = 'z-'*100
		if not phone3: phone3 = 'z-'*100

		#-- 将phone1，phone2匹配到录音记录上去
		# 不能覆盖别人的电话记录
		# sql = 'update core_audiofile set client_sid=?,memo_status=0 ' \
		#       'where client_sid !=? and (phone=? or phone=? or phone=?) and attr!=2'
		sql = 'update core_audiofile set client_sid=?,memo_status=0 ' \
		      'where client_sid =? and (phone=? or phone=? or phone=?) and attr!=2'
		cr = self.db.handle().cursor()
		cr.execute(sql,(self.cur_sid,'',phone1,phone2,phone3) )
		self.db.handle().commit()
		self.close()
		# print repr(self.cur_sid),repr(phone1),repr(phone2),repr(phone3)

		# print 'prarent',self.parent
		if self.parent:
			self.parent.onBtnClientQuery()

	def showClient(self,sid,parent=None):
		self.parent = parent
		self.raise_()
		self.__reset()
		sql = "select * from core_client where sid=?"
		cr = self.db.handle().cursor()
		cr.execute(sql,(sid,))
		r = fetchoneDict(cr)

		self.edtName.setText(r['name'].decode('utf-8'))
		self.cbxSex.setCurrentIndex(int(r['sex']))
		self.edtCorp.setText(r['corp'].decode('utf-8'))
		self.edtPhone1.setText(r['phone1'].decode('utf-8'))
		self.edtPhone2.setText(r['phone2'].decode('utf-8'))
		self.edtAddress.setText(r['address'].decode('utf-8'))
		self.edtPostCode.setText(r['postcode'].decode('utf-8'))
		self.edtMail.setText(r['email'].decode('utf-8'))
#		self.edtWebSite.setText(r['website'].decode('utf-8'))
#		self.edtIm.setText(r['im'].decode('utf-8'))
		self.edtPhone3.setText(r['phone3'].decode('utf-8'))
		self.edtOwnerOrg.setText(r['owner_org'].decode('utf-8'))

		self.cbxType.setCurrentIndex(-1)
		if int(r['type']) < self.cbxType.count():
			self.cbxType.setCurrentIndex(int(r['type']))


		self.edtMemo.setText(r['memo'].decode('utf-8'))
		self.edtPersonId.setText(r['personid'].decode('utf-8'))
		self.edtClientId.setText(r['clientid'].decode('utf-8'))

		self.edtCustomTag.setText(r['custom_tag'].decode('utf-8'))
		self.cur_sid = sid

	def __reset(self):
		self.edtName.setText('')
		self.cbxSex.setCurrentIndex(0)
		self.edtCorp.setText('')
		self.edtPhone1.setText('')
		self.edtPhone2.setText('')
		self.edtAddress.setText('')
		self.edtPostCode.setText('')
		self.edtMail.setText('')
		self.edtPhone3.setText('')
		self.cbxType.setCurrentIndex(0)
		self.edtOwnerOrg.setText('')
#		self.edtWebSite.setText('')
#		self.edtIm.setText('')
		self.edtMemo.setText('')
		self.cur_sid = ''

	def newClient(self,parent=None):
		self.parent=parent
		self.raise_()
		self.__reset()


	def closeEvent(self, event ):
		FormClientInfo.handle = None

if __name__=='__main__':
	pass