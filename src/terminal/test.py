# -*- coding: utf-8 -*-



from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,array,struct,traceback,time,os,sys,os.path


import win32api,win32gui,win32con
import win32event
from base import *

import phone_ipc

term_title=u'领旗语音终端管理'.encode('gbk')
def test_phone_incoming():
	number='13916624477'

	command = struct.pack("30s",number)
	command_pack = array.array("B", command)
	command_info = command_pack.buffer_info()
	cd = struct.pack("LLP", AppConst.PHONE_DIAL, command_info[1], command_info[0])
	cd_pack = array.array("B", cd)
	cd_info = cd_pack.buffer_info()
	hwnd = win32gui.FindWindow(None, term_title)
	print hwnd
	if hwnd:
		win32api.SendMessage(hwnd, win32con.WM_COPYDATA, AppConst.PHONE_INCOMING, cd_info[0])
	else:
		print 'bc not be found!'

def test_phone_recording():
	s='13916624477,0,901'
	command = struct.pack("80s",s)
	command_pack = array.array("B", command)
	command_info = command_pack.buffer_info()
	cd = struct.pack("LLP", AppConst.PHONE_DIAL, command_info[1], command_info[0])
	cd_pack = array.array("B", cd)
	cd_info = cd_pack.buffer_info()
	hwnd = win32gui.FindWindow(None, term_title)
	print hwnd
	if hwnd:
		win32api.SendMessage(hwnd, win32con.WM_COPYDATA, AppConst.PHONE_RECORDING, cd_info[0])
	else:
		print 'bc not be found!'

if __name__=='__main__':
	test_phone_incoming()
	time.sleep(3)
	test_phone_recording()