# -*- coding: utf-8 -*-


from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,time,datetime,traceback,string,json,pickle,os,os.path
from  ui_process_message import *
import utils
from base import *
import dbsql
from dbconn import *




class Form(QtGui.QFrame,Ui_FrameProcessMessage):
	handle = None
	def __init__(self,parent=None):
		QtGui.QFrame.__init__(self,parent)
		self.setupUi(self)
		self.show()
		self.setWindowFlags(Qt.FramelessWindowHint)

	@staticmethod
	def instance(parent=None):
		if not Form.handle:
			Form.handle = Form(parent)
		return Form.handle

	def showProcess(self,title,msg):
		self.setWindowTitle(title)
		self.message.setText(msg)
		self.show()
		self.raise_()

	def closeEvent(self, event):
		self.hide()
		event.ignore()


def show(msg=u'处理中，请等待..',title=''):
	Form.instance().showProcess(title,msg)

def close():
	Form.instance().close()