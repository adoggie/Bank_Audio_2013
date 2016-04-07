# -*- coding: utf-8 -*-


from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,time,datetime,traceback,string,json,pickle,os,os.path
import ui_message
import utils
from base import *



class FormMessage(QtGui.QFrame,ui_message.Ui_FrameMessage):
	_tempvars=[]
	def __init__(self,parent=None):
		QtGui.QFrame.__init__(self,None)
		self.setupUi(self)
		#self.db = dbsql.SqlPrepare()
		self.connect(self.btnOk,SIGNAL('clicked()'),self.onBtnOKClick)
		font = QtGui.QFont(AppConst.APP_FONT_NAME,10)
		self.setFont(font)
		FormMessage._tempvars.append(self)
		flags = self.windowFlags()
		flags &=QtCore.Qt.WindowMinimizeButtonHint #|QtCore.Qt.WindowMaximizeButtonHint
		flags = QtCore.Qt.Dialog

		self.setWindowFlags(flags)

	def onBtnOKClick(self):
		self.close()

	def showMessage(self,title,text):
		self.setWindowTitle(title)
		self.text.setText(text)
		self.show()
		self.raise_()


def about(parent,title,text):
	form = FormMessage(parent)
	form.showMessage(title,text)
	return form

if __name__=='__main__':
	pass