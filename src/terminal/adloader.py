# -*- coding: utf-8 -*-

#adloader.py
#软件加载器

import sys,os,os.path,time,struct,traceback,datetime
import string
import utils
import json,pickle
from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading


import win32api
import win32event

from base import *

class App(QApplication):
	def __init__(self, argv):
		QApplication.__init__(self,argv)
#		rc,msg = taxctrl.init_plugin()
#		if not rc:
#			QMessageBox.about(None,u'错误提示',msg)
#			self.closeAllWindows()
#			sys.exit()

		self.main()
		self.quit()

		# form_usermgr.UserMgr.instance()

	def main(self):
		'''
		1.检测新版本
		'''
		path = getApp().getTempPath()
		files = os.listdir(path)
		for file in files:
			if os.path.isdir(os.path.join(path,file)):
				continue
			#查找软件升级包
			if file.find('.upx') == -1:
				continue
			try:
				self.updateSoftware(os.path.join(path,file))
				file = os.path.join(path,file)
				os.remove(file)
			except:
				traceback.print_exc()
			break
		exe = getApp().getBinPath()+'/leadtel-audio.exe'
		os.system(exe)
#		self.mainwnd = MainWindow(self)

	def updateSoftware(self,file):
		'''
			.upx文件pickle格式
			文件包内:
				version: 0.1.1.0
				files:
					[bin/ffmpeg.exe,binary]
					[bin/local.profile,binary]
					[bin/speex.exe,binary]
					[bin/...,binary]
		'''
		try:
			d = pickle.load(file)
			for file in d.files:
				name,data = file
				#name - 文件名 ; data - 二进制数据
		except:
			traceback.print_exc()
			return False
		return True

	def quit(self):

		QtGui.qApp.quit()

import winerror

hmutex= None
try:
	hmutex = win32event.CreateMutex(None,True,'Mutex-object of Loader of leadtel Audio')
	rc = win32api.GetLastError()
	if rc == winerror.ERROR_ALREADY_EXISTS:
		print 'app is running...'
		hmutex = None
except:
	hmutex = None

if hmutex:
	app = App(sys.argv)
	app.exec_()

