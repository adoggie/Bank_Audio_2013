# -*- coding: utf-8 -*-


from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,time,datetime,traceback,string,json,pickle,os,os.path
from  ui_change_pwd import *
import utils
from base import *
import dbsql
from dbconn import *
import urllib




class FormChangePasswd(QtGui.QDialog,Ui_FrameChangePasswd):
	# handle = None
	def __init__(self,parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.setupUi(self)
		self.db = dbsql.SqlPrepare()
		self.connect(self.btnDone,SIGNAL('clicked()'),self.onBtnDoneClick)
		font = QtGui.QFont(AppConst.APP_FONT_NAME,10)
		self.setFont(font)

		# self.setWindowTitle(u'电话拨号')

	# @staticmethod
	# def instance(parent=None):
	# 	if not FormDial.handle:
	# 		FormDial.handle = FormDial(parent)
	# 	return FormDial.handle



	def onBtnDoneClick(self):
		new1 = self.edt_new.text().toUtf8().data().strip()
		new2 = self.edt_new2.text().toUtf8().data().strip()
		old = self.edt_old.text().toUtf8().data().strip()
		if not old:
			QMessageBox.about(self,u'提示',u'原密码不能为空!')
			return
		if not new1:
			QMessageBox.about(self,u'提示',u'新密码不能为空!')
			return
		if new1 != new2:
			QMessageBox.about(self,u'提示',u'新密码输入不一致!')
			return
		if len(new1)<6:
			QMessageBox.about(self,u'提示',u'新密码长度不能小于6!')
			return

		if not utils.checkPasswdStr(new1):
			QMessageBox.about(self,u'提示',u'新口令必须包含字符和数字!')
			return

		rc = False
		try:
			print 'passwd:',old,new1
			params = urllib.urlencode({'token':getApp().getToken(),'old_pwd':old,'new_pwd':new1})
			server = getApp().getSettings().get('webserver')
			if server.find('http')==-1:
				server = 'http://'+server
			f = urllib.urlopen('%s/WebApi/Terminal/changePwd'%(server),params)   # POST
			d = f.read()
			print 'http request(change passwd): bytes ',len(d)
			d = json.loads(d)
			if d['status'] == 0 :
				rc = True
			print d
		except:
			rc = False
			traceback.print_exc()

		if not rc:
			QMessageBox.about(self,u'提示',u'请求修改登陆密码处理失败!(网络异常或者密码错误)')
			return

		QMessageBox.about(self,u'提示',u'请求 修改登陆密码 操作成功!')
		getApp().setSettingsValue('passwd',new1)
		#getApp().saveSettings()

		self.setSettingsValue('client_passwd_modify_time',str(int(time.time())))
		self.saveSettings()
		self.close()




if __name__=='__main__':
	pass