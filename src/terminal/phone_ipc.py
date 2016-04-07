# -*- coding: utf-8 -*-



from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading


import win32api,win32gui,win32con,struct,array,time
import win32event
from base import *


#'''
#	WM_COPYDATA 传递消息命令
#	{cmd,data}
#	1,10086     DAILING PC -> DEVICE
#	2,          HANGON  PC-> DEVICE  摘机
#	3,          HANGUP  PC-> DEVICE 挂机
#	4,          INCOMING DEVICE -> PC 来电
#   5,10010,0,901          OPENNED  DEVICE->PC 语音建立，开始录音

#	WM_COPYDATA
#	dwData - cmd
#	lpData - data of cmd
#'''

def phoneDial(self,number):
	'''
		电话拨号
	'''
	command = struct.pack("30s",number)
	command_pack = array.array("B", command)
	command_info = command_pack.buffer_info()
	cd = struct.pack("LLP", AppConst.PHONE_DIAL, command_info[1], command_info[0])
	cd_pack = array.array("B", cd)
	cd_info = cd_pack.buffer_info()
	hwnd = win32gui.FindWindow(None, AppConst.WIN_TITLE_BC)
	if hwnd:
		win32api.SendMessage(hwnd, win32con.WM_COPYDATA, AppConst.PHONE_DIAL, cd_info[0])
	else:
		print 'bc not be found!'



def phoneHangOn(self):
	'''
		接电话
	'''

	hwnd = win32gui.FindWindow(None, AppConst.WIN_TITLE_BC)
	if hwnd:
		win32api.SendMessage(hwnd, win32con.WM_COPYDATA, AppConst.PHONE_HANGON, 0)
	else:
		print 'bc not be found!'

def phoneHangUp(self):
	'''
		挂机
	'''
	hwnd = win32gui.FindWindow(None, AppConst.WIN_TITLE_BC)
	if hwnd:
		win32api.SendMessage(hwnd, win32con.WM_COPYDATA, AppConst.PHONE_HANGUP, 0)
	else:
		print 'bc not be found!'

