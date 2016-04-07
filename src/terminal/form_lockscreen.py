# -*- coding: utf-8 -*-


from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,time,datetime,traceback,string,json,pickle,os,os.path
from  ui_lockscreen import *
import utils
from base import *



class FormLockScreen(QtGui.QFrame,Ui_DialogLock):
	handle = None
	signal_close = QtCore.pyqtSignal()
	def __init__(self,parent=None):
		QtGui.QFrame.__init__(self,None)
		self.setupUi(self)
		self.db = dbsql.SqlPrepare()
		self.connect(self.btnUnlock,SIGNAL('clicked()'),self.onBtnUnlockClick)
		# self.connect(self.edtPasswd,SIGNAL('returnPressed()'),self.onEdtPasswdReturn)
		# self.edtPasswd.returnPressed.connect(self.onEdtPasswdReturn)
		# self.signal_close.connect(self.onBtnUnlockClick)
		# getApp().mainwindow.show()
		# self.show()
		# self.setModal(False)
		self.ok = False
		FormLockScreen.handle = self
		flags = self.windowFlags()
		flags &=QtCore.Qt.WindowMinimizeButtonHint #|QtCore.Qt.WindowMaximizeButtonHint
		flags = QtCore.Qt.Dialog

		self.setWindowFlags(flags)
		self.raise_()
		self.timer = QTimer()
		self.connect(self.timer,SIGNAL('timeout()'),self.onTimer)
		self.timer.start(0.3)   #这里很无赖啊，强行将其置前
		self.checkit=False

	def onTimer(self):
		self.raise_()
		# if self.checkit:
		# 	self.onBtnUnlockClick()
		# self.checkit = False

	# def onEdtPasswdReturn(self):
		# self.onBtnUnlockClick()
		# self.checkit = True
		# self.signal_close.emit()

	def keyPressEvent(self,e):
		self.onBtnUnlockClick()
		# print 'aa'

	def onBtnUnlockClick(self):
		passwd = self.edtPasswd.text().toUtf8().data().strip()
		if not passwd:
			QMessageBox.about(self,u'提示',u'错误口令!')
			return
		if getApp().getLockPasswd() == passwd:
			getApp().mainwindow.unlockScreen()
			self.ok = True
			self.close()
			return
		QMessageBox.about(self,u'提示',u'错误口令!')

	def closeEvent(self, event ):
		if not self.ok:
			# event.ignore()
			# if getApp().mainwindow.isVisible():
			# 	getApp().mainwindow.hide()
			event.accept()
			if getApp().mainwindow.isVisible():
				getApp().mainwindow.hide()
		else:
			event.accept()
		FormLockScreen.handle = None

if __name__=='__main__':
	pass