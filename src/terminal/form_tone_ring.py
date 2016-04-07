# -*- coding: utf-8 -*-


from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,time,datetime,traceback,string,json,pickle,os,os.path
from  ui_tone_dial import *
import utils
from base import *
import dbsql
from dbconn import *

import phone_ipc
import utils
import usbcmd
import win32gui, win32con
import win32api

class FormToneRing(QtGui.QFrame,Ui_FrameToneDial):
	handle = None
	def __init__(self,parent=None):
		QtGui.QFrame.__init__(self,parent)
		self.setupUi(self)
		self.db = dbsql.SqlPrepare()
		self.connect(self.btnHangOn,SIGNAL('clicked()'),self.onBtnHangOnClick)
		self.connect(self.btnHangUp,SIGNAL('clicked()'),self.onBtnHangUpClick)
		self.connect(self.btnMemo,SIGNAL('clicked()'),self.onBtnMemoClick)

		self.timer = QTimer()
		self.timer.start(1000*1)
		self.connect(self.timer,SIGNAL('timeout()'),self.onTimer)
		self.elapsed=0

		self.showNormal()
		self.raise_()
		#hWnd = c_ulong(self.winId())
		win32gui.SetWindowPos(self.winId(), win32con.HWND_TOPMOST, 0, 0, 0, 0,
			win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
		self.moveToRightBottom()

		#------
		self.btnMemo.setEnabled(False)
		self.elapsed = 0
		self.txtPhoneNum.clear()
		self.txtClientName.clear()
		self.txtStatus.setText(u'去电..')
		self.txtPhoneNum.setText('')
		self.allow_change = True

	def moveToRightBottom(self):
		screensize = utils.getScreenSize()
		self.move(screensize[0]-self.width()-20,screensize[1]-self.height()-40)

	@staticmethod
	def instance(parent=None):
		if not FormToneRing.handle:
			FormToneRing.handle = FormToneRing(parent)
		return FormToneRing.handle

	def close(self):
		self.newserial_info=()
		QtGui.QFrame.close(self)

	def onTimer(self):
		self.elapsed+=1
		s = utils.formatTimeLength(self.elapsed)
		self.txtDuration.setText(s)

	def onBtnHangOnClick(self):
		usbcmd.UsbHost.instance().phoneHangon()

	def onBtnHangUpClick(self):
		usbcmd.UsbHost.instance().phoneHangup()
#		self.close()

	def showIncomingCall(self,phone):
		self.allow_change = False
		name=''
		self.btnHangOn.setEnabled(True)
		self.labDuration.setVisible(False)
		self.txtDuration.setVisible(False)
		self.elapsed = 0
		self.txtPhoneNum.clear()
		self.txtClientName.clear()
		self.txtStatus.setText(u'来电..')
		self.btnMemo.setEnabled(False)
		if not phone:
			return
		self.txtPhoneNum.setText(phone)

		sql = "select * from core_client where phone1=? or phone2=? or phone3=?"
		cr = self.db.handle().cursor()
		cr.execute(sql,(phone,phone,phone))
		rs = fetchallDict(cr)

		if rs:
			r = rs[0]
			name = r['name']
		self.txtClientName.setText(name.decode('utf-8'))
		self.show()
		self.moveToRightBottom()

	def showOutgoingCall(self,phone,csid=''):
		'''
			csid - client sid
		'''
		self.allow_change = False
		self.btnHangOn.setEnabled(False)
		name=''
		self.elapsed = 0
		self.txtPhoneNum.clear()
		self.txtClientName.clear()
		self.txtStatus.setText(u'去电..')
		self.btnMemo.setEnabled(False)
		if not phone:
			return
		self.txtPhoneNum.setText(phone)

		cr = self.db.handle().cursor()
		if not csid:
			sql = "select * from core_client where (phone1=? or phone2=? or phone3=?) and memo!='<<DELETE>>'"
			cr.execute(sql,(phone,phone,phone))
		else:
			sql = "select * from core_client where sid=? and memo!='<<DELETE>>'"
			cr.execute(sql,(csid,))
		rs = fetchallDict(cr)

		if rs:
			r = rs[0]
			name = r['name']

		self.txtClientName.setText(name.decode('utf-8'))
		self.show()
		self.moveToRightBottom()


	def phoneKeyPress(self,number):
		if not self.allow_change:
			return  #不允许改电话号码
		if not number:
			return
		self.txtClientName.clear()
		self.txtPhoneNum.setText(number)
		cr = self.db.handle().cursor()
		phone = number
		sql = "select * from core_client where (phone1 = ? " \
			      "or phone2 =? or phone3 =?) and memo!='%s'"%AppConst.CLIENT_DELETED_MARKER
		cr.execute(sql,(phone,phone,phone))
		rs = fetchallDict(cr)
		if rs:
			r = rs[0]
			self.txtClientName.setText(r['name'].decode('utf-8'))
		if self.newserial_info:
			self.newserial_info[0] = phone

	def closeEvent(self, event ):
		FormToneRing.handle = None

	def onPhoneNewSerial(self,number,attr,serial):
		'''
			不管 打出还是打入，接通电话都将调用进入
		'''
		self.newserial_info = [number,attr,serial]
		self.btnMemo.setEnabled(True)
		#检查当前是否设置自动弹出备注窗口
		show = getApp().getSettingsValue('memo_auto_show','1')
		show = int(show)
		if show:
			self.onBtnMemoClick() #自动弹出备注窗口
		if attr == AppConst.RECORD_PRESENT:
			self.txtStatus.setText(u'录音')
			self.txtClientName.setText(u'')
			self.txtPhoneNum.setText(u'')


	def onBtnMemoClick(self):
		import form_audio_note

		if not self.newserial_info:
			return
		number,attr,serial = self.newserial_info
		if attr not in (0,1):
			number=''
		note={'spx_index':int(serial),
		      'calltype':int(attr),
		      'phone':number,
		      'duration':0
		}
		#form_tone_ring.FormToneRing.instance().close()  #接听则关闭来电提示窗口
		changable = False
		if int(attr) == 1: #呼出
			changable = True

		form_audio_note.FormAudioNote.instance().showNote(note,changable)


if __name__=='__main__':
	pass