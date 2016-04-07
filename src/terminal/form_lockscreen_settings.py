# -*- coding: utf-8 -*-


from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,time,datetime,traceback,string,json,pickle,os,os.path
from  ui_lockscreen_settings import *
import utils
from base import *


class FormLockSettings(QtGui.QDialog,Ui_DialogLockScreenSettings):
	handle = None
	def __init__(self,parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.setupUi(self)
		self.db = dbsql.SqlPrepare()
		self.connect(self.btnOk,SIGNAL('clicked()'),self.onBtnOkClick)

	def onBtnOkClick(self):
		old = self.edtOld.text().toUtf8().data().strip()
		if not old:
			QMessageBox.about(self,u'提示',u'请输入现有锁屏口令!')
			return
		new = self.edtNew.text().toUtf8().data().strip()
		if not new:
			QMessageBox.about(self,u'提示',u'请输入新的锁屏口令!')
			return
		new2 = self.edtNew2.text().toUtf8().data().strip()
		if new != new2:
			QMessageBox.about(self,u'提示',u'两次新口令不一致!')
			return
		if not utils.checkPasswdStr(new):
			QMessageBox.about(self,u'提示',u'新口令必须包含字符和数字!')
			return

		if getApp().getLockPasswd()!=old:
			QMessageBox.about(self,u'提示',u'输入的旧锁屏口令错误!')
			return
		getApp().setLockPasswd(new)
		self.close()

if __name__=='__main__':
	pass