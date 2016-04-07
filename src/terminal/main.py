# -*- coding: utf-8 -*-

#playctrl.py
#播放控制

from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,time
import utils


import win32api
import win32event
import win32con

import sys,os,datetime,traceback

from form_main import MainWindow

class AudioApp(QApplication):
	def __init__(self, argv):
		QApplication.__init__(self,argv)

		self.main()
		# form_usermgr.UserMgr.instance()

	def main(self):

		# print QApplication.applicationDirPath().toUtf8().data().decode("utf-8").encode("gbk")
		app_path = QApplication.applicationDirPath().toUtf8().data().decode("utf-8")
		if app_path.lower().find('python') == -1:
			os.chdir(app_path)
		self.setQuitOnLastWindowClosed(True)
		self.mainwnd = MainWindow(self)
		self.setQuitOnLastWindowClosed(False)

	# def winEventFilter(self,msg):
	# 	import base
	# 	if msg.message == win32con.WM_MOUSEMOVE:
	# 		if base.getApp().isTimeLocked():
	# 	return False,0


	def quit(self):
		QtGui.qApp.quit()

#
# if len(sys.argv)>=3:
# 	if sys.argv[1] == '-kill':
# 		pid = int(sys.argv[2])


import winerror
hmutex= None
try:
	hmutex = win32event.CreateMutex(None,True,'Mutex-object of audio service')
	rc = win32api.GetLastError()
	if rc == winerror.ERROR_ALREADY_EXISTS:
		print 'app is running...'
		hmutex = None
except:
	hmutex = None

if hmutex:
	h1 = utils.Logger.StdoutHandler(sys.stdout)
	h2 = utils.Logger.DatagramHandler()
	dt = datetime.datetime.now()
	file = "system.%04d-%02d-%02d.log"%(dt.year,dt.month,dt.day)
		
	h3 = utils.Logger.FileHandler(file=file)
	utils.Logger.instance().addHandler(h1)
	utils.Logger.instance().addHandler(h2)
	utils.Logger.instance().addHandler(h3)
	sys.stdout = utils.Logger.instance()


	app = AudioApp(sys.argv)
#	print type(app.applicationDirPath())
	app.exec_()

