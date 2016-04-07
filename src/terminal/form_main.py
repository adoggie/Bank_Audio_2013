# -*- coding: utf-8 -*-
# playconsole.py
# 播放控制台

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ctypes
from ctypes import *

import sys,threading,time,datetime,traceback,string,json,pickle,os,os.path
import array
import win32api
import win32gui
import win32con

from  ui_main import *
import win32api,base64

from dbconn import *

import cipher
import utils
import urllib
from base import *
import message
import network

import filesync

from PyQt4.phonon import Phonon
import dbsql
from dbconn import *
import convert
import form_clientinfo
import archive
import client
import form_processing
import phone_ipc
import form_tone_ring
import form_audio_note

import usbcmd
import form_message

ENCRYPT_KEY='#E0~RweT'

#录音资料检索方式
ARCHIVE_QUERYTYPE_ALL = 0
ARCHIVE_QUERYTYPE_CLIENT = 1
ARCHIVE_QUERYTYPE_PHONE = 2
ARCHIVE_QUERYTYPE_MEMO = 3
ARCHIVE_QUERYTYPE_OPERATOR = 4 #当前录入的客户经理


#录音记录属性
#/来去电属性，0：来电；1：去电 2：录音 3:未接
ARCHIVE_ATTR_ALL = -1
ARCHIVE_ATTR_INCALL = 0
ARCHIVE_ATTR_OUTCALL = 1
ARCHIVE_ATTR_RECORD = 2
ARCHIVE_ATTR_UNREACHED = 3

#客户资料检索类型
CLIENT_QUERYTYPE_ALL = 0
CLIENT_QUERYTYPE_NAME = 1
CLIENT_QUERYTYPE_PHONE = 2
CLIENT_QUERYTYPE_MAIL = 3
CLIENT_QUERYTYPE_MEMO = 4
CLIENT_QUERYTYPE_PERSONID = 5
CLIENT_QUERYTYPE_CLIENTID = 6
CLIENT_QUERYTYPE_CUSTOM_TAG = 7   #客户自定义标签

class PlaySession:
	def __init__(self):
		self.spxfile=''
		self.digest=''
		self.duration=''



class MainWindow(QtGui.QMainWindow,Ui_MainWindow):

	singal_SetTermInfo = pyqtSignal(object)
	signal_phoneRing = pyqtSignal(object)
	signal_phoneNewSerial = pyqtSignal(object,object,object)
	signal_phoneHangon = pyqtSignal()
	signal_phoneHangup = pyqtSignal()
	signal_phoneDial = pyqtSignal(object)
	signal_device_connected = pyqtSignal()  #检测到话机
	signal_device_disconnected = pyqtSignal()
	signal_phonepasswd_status = pyqtSignal(object,object)
	signal_phonering_end = pyqtSignal()  #话机振铃未接 挂断




	def __init__(self,app):
		QtGui.QMainWindow.__init__(self)
		self.setupUi(self)
		self.app = app
		self.db = dbsql.SqlPrepare()
		getApp().mainwindow = self


		self.timer = QTimer()

		self.connect(self.timer,SIGNAL('timeout()'),self.onTimer)

		self.connect(self.btnCheckVersion,SIGNAL('clicked()'),self.onBtnCheckVersionClick)

#		self.connect(self.btnLogin,SIGNAL('clicked()'),self.onBtnLoginClick)

		self.connect(self.ckAutoLogin,SIGNAL('clicked()'),self.onBtnAutoLoginClick)
		self.connect(self.btnSave,SIGNAL('clicked()'),self.onBtnSaveClick)

		self.connect(self.ckAutoStartWithOsStart,SIGNAL('clicked()'),self.onBtnAutoStartWithOsStartClick)
		self.connect(self.btnOpenMediaDir,SIGNAL('clicked()'),self.onBtnOpenMediaDirClick)
		self.connect(self.btnChangePasswd,SIGNAL('clicked()'),self.onBtnChangePasswdClick)
		self.connect(self.btnUpdateTermInfo,SIGNAL('clicked()'),self.onBtnUpdateTermInfoClick)


#		self.connect(self.btnLocalAudioMgr,SIGNAL('clicked()'),self.onBtnLocalAudioMgrClick)


		self.mtxthis = threading.Lock()


		self.init_ui()
		self.init_data()

		self.timer.start(1000*1)

		self.thread = threading.Thread(target=self.work_thread)
		self.thread.start()

		self.connToServer = None

		if getApp().getSettingsValue('runbackground') !=1:
			self.show()
		else:
			self.hide()
#			self.icon.showMessage(u'提示',u'语音程序最小化运行..')
			msg = getApp().getSystemConfig('tray_min_message','').decode('utf-8')
			self.icontray.showMessage(u'提示',msg)
		if not getApp().getSettingsValue('passwd').strip()\
			or not getApp().getSettingsValue('user').strip()\
			or not getApp().getSettingsValue('webserver').strip()\
			or not getApp().getSettingsValue('commserver').strip():
			self.show()
			self.onMenuItem_TabSettings()
			form_message.about(self,u'提示',u'终端登陆用户名、密码和服务器信息不能为空!')
#			QMessageBox.about(self,u'提示',u'系统配置信息不完整!!')

		self.playsession = None

		self.show()

		usbcmd.UsbHost.instance().mediaDir(getApp().getAudioStorePath())
		usbcmd.UsbHost.instance().mainwin = self

		usbcmd.UsbHost.instance().open()

		user,all = self.getDiskFree()
		if user < AppConst.MIN_DISK_FREESPACE : #小于2G
			form_message.about(self,u'提示',u'磁盘空间小于%.3f G,请确保留足够的语音存储空间!'%user)
			self.show()

		self.init_extra()

	def init_extra(self):
		#检查 锁屏密码 和 平台密码修改时间 3个月必须修改
		#lock_passwd_modify_time不存在则写入当前时间
		#
		val = getApp().getSettingsValue('lock_passwd_modify_time',None)
		if not val: #写入当前时间为修改密码时间 (第一次运行)
			getApp().saveSettingsValue('lock_passwd_modify_time',str( int(time.time())))
		else:
			expire =getApp().getSystemConfig('lock_passwd_expire_time','2592000') # 2592000 = 30 days
			expire = int(expire)
			if time.time() - int(val) > expire: #过期，必须修改密码，提示
				form_message.about(None,u'提示',u'锁屏密码过期,请设置新密码!')

		val = getApp().getSettingsValue('client_passwd_modify_time',None)
		if not val: #写入当前时间为修改密码时间 (第一次运行)
			getApp().saveSettingsValue('client_passwd_modify_time',str( int(time.time())))
		else:
			expire =getApp().getSystemConfig('client_passwd_expire_time','2592000') # 2592000 = 30 days
			expire = int(expire)
			if time.time() - int(val) > expire: #过期，必须修改密码，提示
				form_message.about(None,u'提示',u'系统登陆密码过期,请设置新密码!')

		self.checkSoftwareVersion()

	def setTrayIcon(self,type='normal'):
		iconpath=''
		if type=='alert':
			iconpath = os.path.join(getApp().getBinPath(),'resource/images/leadcom_yellow.ico')
		if type=='disable':
			iconpath = os.path.join(getApp().getBinPath(),'resource/images/leadcom_gray.ico')
		else:
			iconpath = os.path.join(getApp().getBinPath(),'resource/images/leadcom.ico')
		try:

			icon = QtGui.QIcon(unicode(iconpath))
			self.icontray.setIcon( icon )
		except:
			traceback.print_exc()

	def init_data(self):
		import utils
		try:
			path = getApp().getTempPath()
			files = os.listdir(path)
			for f in files:
				file = os.path.join(path,f)
				mt = os.path.getmtime(file)
				if int(time.time()) - mt > 3600*24*20:  # 超过20天的临时文件被删除
					print 'remove file(out of date 20 days):',file
					os.remove(file)
		except:
			traceback.print_exc()

		pass


	def onBtnUpdateTermInfoClick(self):
		if not getApp().token:
			QMessageBox.warning(self,u'错误',u'终端未登录到服务器!')
			return
		self.updateTermInfo()

	#2013.7.4
	def onBtnChangePasswdClick(self):
		if not getApp().token:
			QMessageBox.warning(self,u'错误',u'终端未登录到服务器!')
			return
		from form_change_pwd import FormChangePasswd
		form = FormChangePasswd()
		form.exec_()
		self.edtPasswd.setText(getApp().getSettingsValue('passwd',''))



	def onBtnOpenMediaDirClick(self):
		cmd = u"explorer.exe "
		params = [ os.path.normpath(getApp().getAudioStorePath())]
#		print params
#		QProcess.execute(cmd,params)
		params = os.path.normpath(getApp().getAudioStorePath())
		utils.createProcessNoBlock(cmd,params)

	def init_ui(self):
		# set fonts
		font = QtGui.QFont(AppConst.APP_FONT_NAME,10)
		self.setFont(font)
		self.tvClientList.setFont(font)
		self.tvToneList.setFont(font)
		self.tabWidget.setFont(font)

		self.icontray=QSystemTrayIcon()
		iconpath = os.path.join(getApp().getBinPath(),'resource/images/leadcom.ico')
#		print iconpath
#		r=self.icon.isSystemTrayAvailable()
		icon = QtGui.QIcon(unicode(iconpath))
#		self.icontray.setIcon( icon )
		self.setTrayIcon()

		self.icontray.show()

		self.setWindowIcon(icon)

		self.menuExit =QAction(u"退出..",self,triggered=self.exitApp)
		new_m = QMenu()

		actCfg = new_m.addAction(u'语音管理')
		# actAudMgr = new_m.addAction(u'语音管理')
		new_m.addAction(self.menuExit)

		self.icontray.setContextMenu(new_m)

		msg = getApp().getSystemConfig('tray_tip','').decode('utf-8')
		self.icontray.setToolTip(msg)

		self.connect(self.icontray,SIGNAL('activated (QSystemTrayIcon::ActivationReason)'),self.onTrayIconActived)

		self.connect(actCfg,SIGNAL('triggered()'),self.onMenuConfig)
		# self.connect(actAudMgr,SIGNAL('triggered()'),self.onMenuAudioMgr)
		self.connect(self.actionExit,SIGNAL('triggered()'),self.onMenuExit)
		self.connect(self.actLock,SIGNAL('triggered()'),self.onMenuLockScreen)
		self.connect(self.actLockPasswdSetting,SIGNAL('triggered()'),self.onMenuLockScreenSettings)






		msg = getApp().getSystemConfig('win_title','').decode('utf-8')
		self.setWindowTitle(msg)


		self.edtUser.setText(getApp().getSettingsValue('user','').decode('utf-8'))
		self.edtPasswd.setText(getApp().getSettingsValue('passwd',''))
		self.edtServer1.setText(getApp().getSettingsValue('webserver','').decode('utf-8'))
		self.edtServer2.setText(getApp().getSettingsValue('commserver','').decode('utf-8'))

		self.edtPhonePasswd.setText(getApp().getSettingsValue('phone_passwd','0000').decode('utf-8'))

#		self.edtPhone.setText(getApp().getSettingsValue('phone').decode('utf-8'))
#		self.edtEmployee.setText(getApp().getSettingsValue('employee').decode('utf-8'))
#		self.edtAddress.setText(getApp().getSettingsValue('address').decode('utf-8'))
#		self.edtAddition.setText(getApp().getSettingsValue('addition').decode('utf-8'))

		# if getApp().getSettingsValue('startWithOs'):
		if utils.getRegisterValueInAutoRun():
			self.ckAutoStartWithOsStart.setCheckState(2)
		else:
			self.ckAutoStartWithOsStart.setCheckState(0)

#		print getApp().getSettingsValue('runbackground')

		if getApp().getSettingsValue('runbackground'):
			self.ckRunInBackground.setCheckState(2)

		self.ckRunInBackground.setVisible(False)
		self.ckAutoLogin.setVisible(False)

#		self.txtVersion.setText( getApp().getSettingsValue('version').decode('utf-8'))
		self.txtVersion.setText(APP_VER)

		self.singal_SetTermInfo[object].connect(self.setTermInfo)

		self.signal_phoneRing.connect(self.onPhoneIncoming)
		self.signal_phoneNewSerial.connect(self.onPhoneNewSerial)
		self.signal_phoneHangon.connect(self.onPhoneHangOn)
		self.signal_phoneHangup.connect(self.onPhoneHangUp)
		self.signal_phoneDial.connect(self.onPhoneDial)

		self.signal_device_connected.connect(self.onDeviceConnected)
		self.signal_device_disconnected.connect(self.onDeviceDisConnected)

		self.signal_phonepasswd_status.connect(self.onPhonePasswdStatus)

		self.signal_phonering_end.connect(self.onPhoneRingEnd)
#		self.connstatus=u'未认证,未连接'
		# self.tabWidget.removeTab(2)

		self.init_page_archives()
		self.init_page_clients()

		#menus of client
		self.actClientExport.triggered.connect(self.onMenuItem_ClientExport)
		self.actClientImport.triggered.connect(self.onMenuItem_ClientImport)
		self.actClientSyncFromServer.triggered.connect(self.onMenuItem_ClientSyncFromServer)
#		self.actClientSyncToServer.triggered.connect(self.onMenuItem_ClientSyncToServer)
		self.actSyncReset.triggered.connect(self.onMenuItem_SyncReset)

		self.actTabArchive.triggered.connect(self.onMenuItem_TabArchive)
		self.actTabClient.triggered.connect(self.onMenuItem_TabClient)
		self.actTabSettings.triggered.connect(self.onMenuItem_TabSettings)
		self.actTabStatus.triggered.connect(self.onMenuItem_TabStatus)
		self.actAbout.triggered.connect(self.onMenuItem_AppAbout)
		self.actArchiveUnMatched.triggered.connect(self.onMenuItem_ArchiveUnMatched)
		self.actArchiveUnMatchedMutli.triggered.connect(self.onMenuItem_ArchiveUnMatchedMulti)
		self.actArchiveExport.triggered.connect(self.onMenuItem_ArchiveExport)

		self.btnLogin.setVisible(False)

		self.tabRunLog.setVisible(False)
		self.label_11.setVisible(False )    # config server2 - label
		self.edtServer2.setVisible(False)   # config server2 - edit
		self.btnBack.setVisible(False)
		self.btnNext.setVisible(False)

		tabidx = self.tabWidget.indexOf(self.tabRunLog)
		self.tabWidget.removeTab(tabidx)

		self.passwdmatched = False


		self.cbxLockTimes.addItem(u'1分钟',60*1)
		self.cbxLockTimes.addItem(u'5分钟',60*5)
		self.cbxLockTimes.addItem(u'15分钟',60*15)
		self.cbxLockTimes.addItem(u'30分钟',60*30)

		self.cbxLockTimes.addItem(u'关闭',60*60*24*30)
		for n in range(self.cbxLockTimes.count()):
			d,ok = self.cbxLockTimes.itemData(n).toInt()
			if d >= getApp().lock_cycle:
				self.cbxLockTimes.setCurrentIndex(n)
				getApp().setTimeLockCycle(d)
				break

		self.connect(self.cbxLockTimes,SIGNAL('currentIndexChanged(int)'),self.onChangeTimeLock)


		self.connect(self.ckMemoAutoShow,SIGNAL('clicked()'),self.onBtnMemoAutoShowClick)
		if int(getApp().getSettingsValue('memo_auto_show','1')) != 0:
			self.ckMemoAutoShow.setCheckState(2)
		else:
			self.ckMemoAutoShow.setCheckState(0)


	def onBtnMemoAutoShowClick(self):
		print 'onBtnMemoAutoShowClick ..'
		if self.ckMemoAutoShow.checkState() == 0 :
			getApp().saveSettingsValue('memo_auto_show','0')
		else:
			getApp().saveSettingsValue('memo_auto_show','1')


	def onChangeTimeLock(self,index):
		if index != self.cbxLockTimes.count()-1:
			passwd = getApp().getLockPasswd()
			if not passwd or passwd=='111111':
				QMessageBox.about(self,u'提示',u'锁屏密码未设置，锁屏功能无法启动!')
				self.cbxLockTimes.setCurrentIndex(self.cbxLockTimes.count()-1)
				return
		d,ok = self.cbxLockTimes.itemData(index).toInt()
		getApp().setTimeLockCycle(d)

	def onPhonePasswdStatus(self,succ,passwd):
		self.passwdmatched = succ
		if not self.passwdmatched:
			self.txtPhonePasswdStatus.setText(u'话机密码设置错误!')
		else:
			self.txtPhonePasswdStatus.setText(u'密码正确')


	def onMenuItem_SyncReset(self):
		'''
			同步话机计数
		'''
		msg =u'是否确定重新同步话机所有语音资料到PC机？'
		if QMessageBox.No == QMessageBox.question(self,u'提示',msg,QMessageBox.Yes|QMessageBox.No,QMessageBox.No):
			return
		usbcmd.UsbHost.instance().currentSerial(0)

	def onMenuItem_AppAbout(self):
		QMessageBox.about(self,u'关于',u'领旗语音终端系统\n版本:%s\n日期:%s'%
			(APP_VER,BUILD_TIME)
			)


	def onMenuItem_TabArchive(self):
		idx = self.tabWidget.indexOf(self.tabArchives)
		self.tabWidget.setCurrentIndex(idx)

	def onMenuItem_TabClient(self):
		idx = self.tabWidget.indexOf(self.tabClients)
		self.tabWidget.setCurrentIndex(idx)

	def onMenuItem_TabSettings(self):
		idx = self.tabWidget.indexOf(self.tabSettings)
		self.tabWidget.setCurrentIndex(idx)


	def onMenuItem_TabStatus(self):
		idx = self.tabWidget.indexOf(self.tabStatus)
		self.tabWidget.setCurrentIndex(idx)


	def onDeviceConnected(self):
		'''
			检测到话机，通知
		'''
		print 'usb phone detected!'
		self.txtPhoneStatus.setText(u'在线')
#		QMessageBox.about(self,u'提示',u'已检测到usb话机!')

	def onDeviceDisConnected(self):
		''' 话机丢失
		'''
		print 'usb phone losted!'
		self.txtPhoneStatus.setText(u'离线')
		if self.isVisible() and self.isEnabled():
			form_message.about(self,u'提示',u'usb话机丢失!')

	def onMenuItem_ClientExport(self):
		file = QFileDialog.getSaveFileName(self,u'选择导出文件','',u'客户信息(*.xls)')
		if not file:
			return
		#生成输出文件
		file = file.toUtf8().data().decode('utf-8')
		import client
		rc = client.export_to_xls(file,self.db.handle())
		if not rc:
			QMessageBox.about(self,u'提示',u'导出失败!')
			return
		QMessageBox.about(self,u'提示',u'导出okay')


	def onMenuItem_ClientImport(self):
		#导入客户信息



		import client

		msg = u"导入客户信息将更改和替换原有的客户信息列表，是否继续?"
		if QMessageBox.No == QMessageBox.question(getApp().mainwindow,u'提示',msg,QMessageBox.Yes|QMessageBox.No,
	                                          QMessageBox.No):
			return

		file = QFileDialog.getOpenFileName(None,u'选择输入文件','',u'客户信息(*.xls)')
		if not file:
			return
		file = file.toUtf8().data().decode('utf-8')
		rc = client.import_from_xls(file,self.db.handle())
		if not rc:
			QMessageBox.about(self,u'提示',u'导入失败!')
			return
		QMessageBox.about(self,u'提示',u'导入okay')
		self.onBtnClientQuery()


	def onMenuItem_ClientSyncFromServer(self):
		#从服务器获取客户信息
		token = getApp().getToken()
		if not token:
			QMessageBox.about(self,u'提示',u'尚未注册到服务器!')
			return
		import client
		self.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
		r = client.syncFromServer(self.db.handle())
		self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
		if not r:
			QMessageBox.about(self,u'提示',u'操作失败!')
			return
		QMessageBox.about(self,u'提示',u'操作成功!')


	def onMenuItem_ClientSyncToServer(self):
		#将客户信息同步上传到服务器
		token = getApp().getToken()
		if not token:
			QMessageBox.about(self,u'提示',u'尚未注册到服务器!')
			return
		import client
		self.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
		r = client.syncToServer(self.db.handle())
		self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
		if not r:
			QMessageBox.about(self,u'提示',u'操作失败!')
			return
		QMessageBox.about(self,u'提示',u'操作成功!')



	def onBtnDial(self):
		import form_dial
		form = form_dial.FormDial.instance(None)
		form.showPhoneNum2('')

	def onBtnHangup(self):
		usbcmd.UsbHost.instance().phoneHangup()
		pass


	def init_page_clients(self):

		self.connect(self.btnDial,SIGNAL('clicked()'),self.onBtnDial)
		self.connect(self.btnHangup,SIGNAL('clicked()'),self.onBtnHangup)


		self.cbxClientQueryTypes.addItem(u'  ------ 全部 ------',CLIENT_QUERYTYPE_ALL)
		self.cbxClientQueryTypes.addItem(u'  客户名称',CLIENT_QUERYTYPE_NAME)
		self.cbxClientQueryTypes.addItem(u'  身份证编号',CLIENT_QUERYTYPE_PERSONID)
		self.cbxClientQueryTypes.addItem(u'  客户ID',CLIENT_QUERYTYPE_CLIENTID)

		self.cbxClientQueryTypes.addItem(u'  电话号码',CLIENT_QUERYTYPE_PHONE)
		self.cbxClientQueryTypes.addItem(u'  邮件',CLIENT_QUERYTYPE_MAIL)
		self.cbxClientQueryTypes.addItem(u'  备注',CLIENT_QUERYTYPE_MEMO)
		self.cbxClientQueryTypes.addItem(u'  自定义标签',CLIENT_QUERYTYPE_CUSTOM_TAG)


		self.cbxClientType.addItem(u'所有类型',0xff)
		for k,v in AppConst.CLIENT_TYPES:
			self.cbxClientType.addItem(v,k)
		self.cbxClientType.setCurrentIndex(0)

		self.tvClientList.setHeaderLabels([
			u'序号',
		    u'客户名称',
		    u'身份证号',
		    u'客户ID号',
		    u'性别',
		    u'公司',
		    u'电话1',
			u'电话2',
			u'电话3',

		    u'客户类别',
		    u'归属机构',
		    u'备注说明',
		    u'自定义标签',

		    u'地址',
		    u'邮编',
		    u'邮件',

		    u'',
		])

		self.tvClientList.resizeColumnToContents(0)
		self.connect(self.tvClientList,SIGNAL('itemDoubleClicked(QTreeWidgetItem*,int)'),self.onTreeItemDblClick_Clients)
		self.connect(self.tvClientList,SIGNAL('itemClicked(QTreeWidgetItem*,int)'),self.onTreeItemClick_Clients)
		self.idxdata_clients={}    # {ti:spx_digest}

		self.connect(self.btnClientQuery,SIGNAL('clicked()'),self.onBtnClientQuery)
		self.connect(self.btnClientNew,SIGNAL('clicked()'),self.onBtnClientNew)
		self.connect(self.btnClientEdit,SIGNAL('clicked()'),self.onBtnClientEdit)
		self.connect(self.btnClientDelete,SIGNAL('clicked()'),self.onBtnClientDelete)
#		self.connect(self.btnClientDial,SIGNAL('clicked()'),self.onBtnClientDial)
		#录音拨号
		self.connect(self.btnRecordDial,SIGNAL('clicked()'),self.onBtnRecordDial)

		self.tvClientList.customContextMenuRequested.connect(self.tvClientList_openMenu)
		self.tvClientList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.tvClientList.setAlternatingRowColors(True)
		self.onBtnClientQuery()

		self.connect(self.btnSceneRecordStart,SIGNAL('clicked()'),self.onBtnSceneRecordStart)
		self.connect(self.btnSceneRecordStop,SIGNAL('clicked()'),self.onBtnSceneRecordStop)

	def onBtnSceneRecordStart(self):
		print 'record start..'
		usbcmd.UsbHost.instance().recordStart()

	def onBtnSceneRecordStop(self):
		print 'record stop..'
		usbcmd.UsbHost.instance().recordStop()

	def onBtnClientQuery(self):
		text = self.edtClientQueryContent.text().toUtf8().data().strip().lower()
		type = self.cbxClientQueryTypes.itemData(self.cbxClientQueryTypes.currentIndex()).toInt()[0]
		sql = "select * from core_client where 1=1 and memo<>'<<DELETE>>' "
		if type == CLIENT_QUERYTYPE_NAME:
			sql+=" and (name like '%%%s%%' or pinyin like '%%%s%%' or clientid like '%%%s%%' ) "%(text,text,text)
		if type == CLIENT_QUERYTYPE_PHONE:
			sql+= " and (phone1 like '%%%s%%' or phone2 like '%%%s%%' or phone3 like '%%%s%%') "%(text,text,text)
		if type == CLIENT_QUERYTYPE_MAIL:
			sql+=" and email like '%%%s%%'" %text
		if type == CLIENT_QUERYTYPE_MEMO:
			sql+=" and memo like '%%%s%%' "%text
		if type == CLIENT_QUERYTYPE_PERSONID:
			sql+=" and personid like '%%%s%%' "%text
		if type == CLIENT_QUERYTYPE_CLIENTID:
			sql+=" and clientid like '%%%s%%' "%text

		#2013.11.8
		if type == CLIENT_QUERYTYPE_CUSTOM_TAG: #自定义标签
			sql+=" and custom_tag like '%%%s%%' "%text


		type = self.cbxClientType.itemData(self.cbxClientType.currentIndex()).toInt()[0]
		if type != 0xff:
			sql+=' and type=%s '%type

		sql+= ' order by pinyin '
		cr = self.db.handle().cursor()
		cr.execute(sql)
		rs = fetchallDict(cr)
		self.idxdata_clients={}
		self.tvClientList.clear()
		idx = 0
		for r in rs:
			idx+=1
			sex = u'男'
			if int(r['sex'])!=1:
				sex = u'女'

			row = ('%02d '%idx,
					r['name'].decode('utf-8')+'  ',
			        r['personid'].decode('utf-8')+' ',
			        r['clientid'].decode('utf-8')+' ',
					sex,
			        r['corp'].decode('utf-8')+' ',
			        r['phone1'].decode('utf-8')+' ',
			        r['phone2'].decode('utf-8')+' ',
			        r['phone3'].decode('utf-8')+' ',

			        AppConst.getClientTypeName(r['type'])+' ',  #客户类别
			        r['owner_org'].decode('utf-8')+' ', #归属机构
			        r['memo'].replace('\n', ' ').decode('utf-8')+' ',
			        r['custom_tag'].decode('utf-8')+' ',

			         r['address'].decode('utf-8')+' ',
			        r['postcode'].decode('utf-8')+' ',
			        r['email'].decode('utf-8')+' ',

				)
			ti = QTreeWidgetItem(row )
			self.tvClientList.addTopLevelItem(ti)
			self.idxdata_clients[ti] = r['sid']
		if rs:
			self.tvClientList.resizeColumnToContents(0)
			self.tvClientList.resizeColumnToContents(1)
			self.tvClientList.resizeColumnToContents(2)


	def onBtnClientNew(self):
		form = form_clientinfo.FormClientInfo.instance()
		form.newClient(self)

	def onBtnClientEdit(self):
		tis = self.tvClientList.selectedItems()
#		print tis
		if not tis:
			return
		ti = tis[0]
		form = form_clientinfo.FormClientInfo.instance()
		form.showClient(self.idxdata_clients[ti],self)
#		print form

	# 2013.7.5
	#  1. 支持批量删除
	def onBtnClientDelete(self):
		tis = self.tvClientList.selectedItems()
		if not tis:
			QMessageBox.about(self,u'提示',u'请选择客户记录!')
			return
		msg = u'您选择的%s项客户记录将被删除,是否真的删除?'%len(tis)
		if QMessageBox.No == QMessageBox.question(self,u'提示',msg,QMessageBox.Yes|QMessageBox.No,QMessageBox.No):
			return
		cr = self.db.handle().cursor()
		for ti in tis:
			sid = self.idxdata_clients.get(ti)
			if not sid:
				continue

			#检查客户关联的录音记录

			# sql =' select count(*) as cnt from core_audiofile where client_sid=?'
			# cr.execute(sql,(sid,))
			# r = fetchoneDict(cr)
			#sql = 'delete from core_client where sid=?'
			sql = "update  core_client set status = 0 ,memo='<<DELETE>>' where sid=?"
			cr = self.db.handle().cursor()
			cr.execute(sql,(sid,))
			sql = "update core_audiofile set client_sid='' where client_sid=?"
			cr.execute(sql,(sid,))

			idx = self.tvClientList.indexOfTopLevelItem(ti)
			self.tvClientList.takeTopLevelItem(idx)
			del self.idxdata_clients[ti]
			# self.onBtnClientQuery()
		self.db.handle().commit()
		print 'client records: %s has been remove!'%len(tis)

	def onTreeItemClick_Clients(self,ti,col):

		sid = self.idxdata_clients[ti]
		if form_clientinfo.FormClientInfo.handle:
			form_clientinfo.FormClientInfo.handle.showClient(sid,self)
		pass

	def onTreeItemDblClick_Clients(self,ti,col):
		#双击等同于编辑
		print 'double click'
		self.onBtnClientEdit()

	def onBtnRecordDial(self):
		tis = self.tvToneList.selectedItems()
		if not tis:
			return


	def tvClientList_openMenu(self,position):
		tis = self.tvClientList.selectedItems()
		if not tis:
			return
		ti = tis[0]
		sid = self.idxdata_clients[ti]
		cr = self.db.handle().cursor()
		cr.execute('select * from core_client where sid=?',(sid,))
		rs = fetchallDict(cr)
		if not rs: return

		text = rs[0]['name'].decode('utf-8')

		menu = QMenu()
		actDial = menu.addAction(u"拨号")
		actToneHistory = menu.addAction(u'通话历史')
		action = menu.exec_(self.tvClientList.mapToGlobal(position))
		if action == actDial:
			import form_dial
			form = form_dial.FormDial.instance(None)
			form.showPhoneNum(sid)

		if action == actToneHistory:
			#切换到通话记录界面
			self.edtToneQueryContent.setText(text)
			self.cbxToneQueryTypes.setCurrentIndex(1)
			self.onBtnArchiveQuery()
			idx = self.tabWidget.indexOf(self.tabArchives)
			self.tabWidget.setCurrentIndex(idx)


	def init_page_archives(self):
		self.init_audio()
		curtime = QDateTime.currentDateTime ()


		t = time.localtime()
		secs = time.mktime((t.tm_year,t.tm_mon,t.tm_mday,0,0,0,0,0,0))
		curtime.setTime_t(int(secs))
		self.dtToneStart.setDateTime(curtime)
		curtime = curtime.addDays(1)

		self.dtToneEnd.setDateTime(curtime)
		#curtime = curtime.addYears(-4)
		curtime = curtime.addMonths(-1)

		self.dtToneStart.setDateTime(curtime)

		self.cbxToneQueryTypes.addItem(u'  ------ 全部 ------',ARCHIVE_QUERYTYPE_ALL)
		self.cbxToneQueryTypes.addItem(u'  客户名称/ID',ARCHIVE_QUERYTYPE_CLIENT)
		self.cbxToneQueryTypes.addItem(u'  电话号码',ARCHIVE_QUERYTYPE_PHONE)


		self.cbxToneAttrs.addItem(u'  -- 全 部 --',ARCHIVE_ATTR_ALL)
		self.cbxToneAttrs.addItem(u'  来 电',ARCHIVE_ATTR_INCALL)
		self.cbxToneAttrs.addItem(u'  去 电',ARCHIVE_ATTR_OUTCALL)
		self.cbxToneAttrs.addItem(u'  录 音',ARCHIVE_ATTR_RECORD)


		self.cbxToneType.addItem(u'   -- 全 部 --',AppConst.valueToStr)
		#self.cbxToneType.addItem(AppConst.valueToStr(AppConst.ARCHIVE_NOTE_TYPE_NORMAL),AppConst.ARCHIVE_NOTE_TYPE_NORMAL)
		#self.cbxToneType.addItem(AppConst.valueToStr(AppConst.ARCHIVE_NOTE_TYPE_SALE),AppConst.ARCHIVE_NOTE_TYPE_SALE)
		#self.cbxToneType.addItem(AppConst.valueToStr(AppConst.ARCHIVE_NOTE_TYPE_OTHER),AppConst.ARCHIVE_NOTE_TYPE_OTHER)
		keys = AppConst.tone_types.keys()
		keys.sort()
		for k in keys:
			self.cbxToneType.addItem(AppConst.valueToStr(k),k)


		self.tvToneList.setHeaderLabels([
			u'序号',
		    u'通话时间',
		    u'电话号码',
		    u'客户名称',
#		    u'身份证ID',
		    u'客户ID',
		    # u'录音类型',
		    u'来去电类型',
		    u'通话类型',
			u'通话时长',
		    u'客户经理', # 2013.10.9
		    u'同步状态',
		    u'产品ID',
		    u'备注',
		    u'',
		])
		#self.listRecords.setHorizontalHeaderLabels(['a','b'])
		self.tvToneList.resizeColumnToContents(0)
		self.connect(self.tvToneList,SIGNAL('itemDoubleClicked(QTreeWidgetItem*,int)'),self.onTreeItemDblClick_Archives)
		self.idxdata_archives={}    # {ti:spx_digest}

		self.connect(self.btnToneQuery,SIGNAL('clicked()'),self.onBtnArchiveQuery)
		#录音拨号
#		self.connect(self.btnRecordDial,SIGNAL('clicked()'),self.onBtnRecordDial)
		self.connect(self.btnToneMemo,SIGNAL('clicked()'),self.onBtnToneMemoClick)

		self.tvToneList.customContextMenuRequested.connect(self.tvToneList_openMenu)
		self.tvToneList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.tvToneList.setAlternatingRowColors(True)

		self.btnRecordDial.setVisible(False)

		self.currentPlaySpxDigest=''

	def tvToneList_openMenu(self,position):
		tis = self.tvToneList.selectedItems()
		phone = ''
		if not tis:
			return
		ti = tis[0]
		menu = QMenu()
		actPlay = menu.addAction(u'播放')
		actDial = menu.addAction(u"拨号")
		actMemo = menu.addAction(u'修改备注')
		action = menu.exec_(self.tvToneList.mapToGlobal(position))
		if action == actDial:
			self.onBtnToneRecordDial()
		if action == actPlay:
			self.onBtnPlayClick()
		if action == actMemo:
			digest = self.idxdata_archives[ti]
			self.showToneRecordMemo(digest)

	def showToneRecordMemo(self,digest):
		import form_audio_note
		form = form_audio_note.FormAudioNote.instance()
		note={'spx_digest':digest}
		form.showNote(note)

	def onBtnToneMemoClick(self):
		# if not self.currentPlaySpxDigest:
		# 	return
		ti = self.tvToneList.currentItem()
		if not ti:
			return
		digest = self.idxdata_archives.get(ti)
		if digest:
			self.showToneRecordMemo(digest)

	#刷新录音记录信息
	def onArchiveNoteEdit(self,digest):
		cr = self.db.handle().cursor()
		sql = "select * from core_audiofile where digest=?"
		cr.execute(sql,(digest,))
		r = fetchoneDict(cr)
		if not r:
			return
		# QMessageBox.about(self,u'提示',u'p1')
		ti = None
		for k,d in self.idxdata_archives.items():
			if d == digest:
				ti = k
				break
		if not ti:
			return
		# QMessageBox.about(self,u'提示',u'p2')
		tonetime = utils.formatTimestamp_ymdhm(r['filetime'])
		phone = r['phone']
		attr = u'未知'
		if r['attr'] == 0 :
			attr=u'来电'
		elif r['attr'] == 1:
			attr=u'去电'
		elif r['attr'] == 2:
			attr=u'录音'
		elif r['attr'] == 3:
			attr = u'未接'
		duration = r['duration']
		duration = utils.formatTimeLength(duration)
		memo = r['memo'].replace('\n',' ')
		client = ''
		personid = ''
		clientid =''
		operator=''
		if r['client_sid']:
				sql = 'select * from core_client where sid = ?'
				cr = self.db.handle().cursor()
				cr.execute(sql,(r['client_sid'],))
				clients = fetchallDict(cr)
				if clients:
					client = clients[0]['name']
					personid = clients[0]['personid']
					clientid = clients[0]['clientid']

		synced = u'未上传'
		if r['status']:
			synced = u'已上传'

		tonetype = AppConst.valueToStr(r['type'])
		productid = r['productid'].decode('utf-8')
		operator = utils.normalizeString(r['operator']).decode('utf-8')
		row = (
				tonetime+' '*2,
				phone.decode('utf-8')+'  ',
		       client.decode('utf-8')+' ',
#			       personid.decode('utf-8'),
		       clientid.decode('utf-8')+' ',
		       attr,
			       tonetype,
		       duration,
               operator,
		       synced,
		       productid+' ',
		       memo.decode('utf-8')
			)
		n=1
		for p in  row:
			ti.setText(n,p)
			n+=1
			#QMessageBox.about(self,u'提示',p)
			# print p.encode('gbk')



	def onBtnToneRecordDial(self):
		'''
			录音资料文件拨号
		'''
		tis = self.tvToneList.selectedItems()
		phone = ''
		if tis:
			ti = tis[0]
			digest = self.idxdata_archives[ti]
			sql = 'select * from core_audiofile where digest=?'
			cr = self.db.handle().cursor()
			cr.execute(sql,(digest,))
			r = fetchoneDict(cr)
			phone = r['phone']

		#显示拨号窗口
		import form_dial
		form = form_dial.FormDial.instance(None)
		form.showPhoneNum2(phone)
		pass


	def onBtnArchiveQuery(self):
		'''
			点击查询录音资料
		'''
		text = self.edtToneQueryContent.text().toUtf8().data().strip().lower()
		memo = self.edtToneQueryMemo.text().toUtf8().data().strip()

		type = self.cbxToneQueryTypes.itemData(self.cbxToneQueryTypes.currentIndex()).toInt()[0]

		sql = 'select a.* from core_audiofile a where 1=1  '
		if type == ARCHIVE_QUERYTYPE_CLIENT:
			if text:
				sql="select a.* from core_audiofile a,core_client b where a.client_sid=b.sid  and b" \
				    ".memo!='%s'"%AppConst.CLIENT_DELETED_MARKER
				sql+=" and ( (b.name like '%%%s%%') or (b.clientid like '%%%s%%') or " \
				     "(b.pinyin like '%%%s%%') )"%(
				text,text,text)
		elif type == ARCHIVE_QUERYTYPE_PHONE:
			if text:
				sql += " and  (a.phone like '%%%s%%' ) "%(text)

		attr = self.cbxToneAttrs.itemData(self.cbxToneAttrs.currentIndex()).toInt()[0]

		type = self.cbxToneType.itemData(self.cbxToneType.currentIndex()).toInt()[0]

		if type!= AppConst.ARCHIVE_NOTE_TYPE_ALL:
			sql+=" and a.type=%s "%type


		if memo:
			sql+=" and (a.memo like '%%%s%%' or a.productid like '%%%s%%' or a.operator like '%%%s%%') "%(memo,memo,memo)

		if attr !=  ARCHIVE_ATTR_ALL:
			sql+=' and a.attr=%s '%attr
		start = self.dtToneStart.dateTime().toTime_t ()
		end = self.dtToneEnd.dateTime().toTime_t ()
		sql+=' and (filetime between %s and %s)'%(start,end)
		sql+=' order by filetime desc,serial desc limit 500'
		cr = self.db.handle().cursor()
		cr.execute(sql)
		rs = fetchallDict(cr)
		idx = 0
		print sql
		self.tvToneList.clear()
		self.idxdata_archives={}



		for r in rs:

			#----- 删除不存在的记录 --------

			if getApp().getSystemConfig('remove_unresolved_record','0') == '1':
				if not os.path.exists(r['spxfile'].decode('utf-8')):
					cr = self.db.handle().cursor()
					cr.execute('delete from core_audiofile where digest=?',(r['digest'],))
					self.db.handle().commit()
					continue
			#----- END --------

			idx+=1
			tonetime = utils.formatTimestamp(r['filetime'])
			phone = r['phone']
			attr = u'未知'
			if r['attr'] == 0 :
				attr=u'来电'
			elif r['attr'] == 1:
				attr=u'去电'
			elif r['attr'] == 2:
				attr=u'录音'
			elif r['attr'] == 3:
				attr = u'未接'
			duration = r['duration']
			duration = utils.formatTimeLength(duration)
			memo = r['memo'].replace('\n',' ')
			client = ''
			personid = ''
			clientid =''
			operator=''
			if r['client_sid']:
				sql = 'select * from core_client where sid = ?'
				cr = self.db.handle().cursor()
				cr.execute(sql,(r['client_sid'],))
				clients = fetchallDict(cr)
				if clients:
					client = clients[0]['name']
					personid = clients[0]['personid']
					clientid = clients[0]['clientid']
			synced = u'未上传'
			if r['status']:
				synced = u'已上传'

			tonetype = AppConst.valueToStr(r['type'])
			productid = r['productid'].decode('utf-8')
			operator = utils.normalizeString(r['operator']).decode('utf-8')
			row = ('%02d '%idx,
					tonetime+' '*2,
					phone.decode('utf-8')+'  ',
			       client.decode('utf-8')+' ',
#			       personid.decode('utf-8'),
			       clientid.decode('utf-8')+' ',
			       attr,
			       tonetype,
			       duration,
					operator, # 业务经理 2013.10.9
			       synced,
			       productid+' ',
			       memo.decode('utf-8')
				)
			ti = QTreeWidgetItem(row )
			self.tvToneList.addTopLevelItem(ti)
			self.idxdata_archives[ti] = r['digest']


		self.tvToneList.resizeColumnToContents(0)
		self.tvToneList.resizeColumnToContents(1)
		self.tvToneList.resizeColumnToContents(2)
		self.tvToneList.resizeColumnToContents(3)


	def playPrepare(self,spx_digest):
		'''
			播放将进行spx到wav的转换
		'''

#		form_processing.show(u'处理中，请等待..')
#
#		for n in range(10):
#			utils.Win32.dispatchMessage(self.winId())
#			time.sleep(1)
#
##		form_processing.close()
#		return

		wav = os.path.join(getApp().getTempPath(),spx_digest+'.wav' )
#		mp3 = os.path.join(getApp().getTempPath(),spx_digest+'.mp3' )
		if not os.path.exists(wav):  # convert spx to wav
			sql = 'select * from core_audiofile where digest=?'
			cr = self.db.handle().cursor()
			cr.execute(sql,(spx_digest,))
			rs = fetchallDict(cr)
			spxfile = rs[0]['spxfile']

			print spxfile
			if not os.path.exists(spxfile.decode('utf-8')):
				return False

			self.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
			form_processing.show(u'处理中，请等待..')
			try:
				convert.spx_convert_wav(spxfile.decode('utf-8'),wav,'1')
			except:pass

			form_processing.close()

			self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
		if not os.path.exists(wav):
			QMessageBox.about(self,u'提示',u'无法获取语音数据!')
			return False

		source = Phonon.MediaSource(wav)
		self.mediaObject.setCurrentSource(source)
		self.mediaObject.play()

		sql = 'select * from core_audiofile where digest=?'
		cr = self.db.handle().cursor()
		cr.execute(sql,(spx_digest,))
		rs = fetchallDict(cr)
		if rs:
			r = rs[0]
			self.txtTonePhone.setText(r['phone'])
			self.txtToneTime.setText(utils.formatTimestamp(r['filetime']))

		self.currentPlaySpxDigest= spx_digest


	def onTreeItemDblClick_Archives(self,ti,col):
		spx = self.idxdata_archives.get(ti)
		if not spx:
			return

		wasPlaying = (self.mediaObject.state() == Phonon.PlayingState)
		self.mediaObject.stop()
		self.mediaObject.clearQueue()

		self.playPrepare(spx)
#		self.mediaObject.setCurrentSource(self.sources[row])

#		if wasPlaying:
#		self.mediaObject.play()
#		else:
#			 self.mediaObject.stop()

	def init_audio(self):
		# img_play = QtGui.QIcon('./resource/images/play.bmp')
		# img_pause = QtGui.QIcon('./resource/images/pause.bmp')
		# img_stop = QtGui.QIcon('./resource/images/stop.bmp')
		# img_back = QtGui.QIcon('./resource/images/previous.bmp')
		# img_next = QtGui.QIcon('./resource/images/next.bmp')
		img_play = self.style().standardIcon(QtGui.QStyle.SP_MediaPlay)
		img_pause = self.style().standardIcon(QtGui.QStyle.SP_MediaPause)
		img_stop = self.style().standardIcon(QtGui.QStyle.SP_MediaStop)
		img_back = self.style().standardIcon(QtGui.QStyle.SP_MediaSkipBackward)
		img_next = self.style().standardIcon(QtGui.QStyle.SP_MediaSkipForward)



		self.btnPlay.setIcon(img_play)
		self.btnPause.setIcon(img_pause)
		self.btnStop.setIcon(img_stop)
		self.btnBack.setIcon(img_back)
		self.btnNext.setIcon(img_next)


		self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
		self.mediaObject = Phonon.MediaObject(self)
		self.metaInformationResolver = Phonon.MediaObject(self)

		self.mediaObject.setTickInterval(1000)

		self.mediaObject.tick.connect(self.tick)
		self.mediaObject.stateChanged.connect(self.stateChanged)
		self.metaInformationResolver.stateChanged.connect(self.metaStateChanged)
		self.mediaObject.currentSourceChanged.connect(self.sourceChanged)
		self.mediaObject.aboutToFinish.connect(self.aboutToFinish)

		Phonon.createPath(self.mediaObject, self.audioOutput)

		self.seekSlider.setMediaObject(self.mediaObject)
		self.volumeSlider.setAudioOutput(self.audioOutput)
		self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,
				QtGui.QSizePolicy.Maximum)


		self.connect(self.btnPlay,SIGNAL('clicked()'),self.onBtnPlayClick)
		self.connect(self.btnPause,SIGNAL('clicked()'),self.onBtnPauseClick)
		self.connect(self.btnStop,SIGNAL('clicked()'),self.onBtnStopClick)
		self.connect(self.btnNext,SIGNAL('clicked()'),self.onBtnNextClick)
		self.connect(self.btnBack,SIGNAL('clicked()'),self.onBtnBackClick)





	def onBtnPauseClick(self):
		self.mediaObject.pause()

	def onBtnStopClick(self):
		self.mediaObject.stop()

	def onBtnNextClick(self):
		'''

		'''
#		idxes = self.tvToneList.selectedIndexes()
#		if not idxes:
#			return
#		idx = idxes[0]
#		print idxes
#
#		if idx == self.tvToneList.topLevelItemCount()-1:
#			return # reached end
#		ti = self.tvToneList.topLevelItem(idx+1)
#		self.tvToneList.setCurrentItem(ti)
#		self.onBtnStopClick()
#		self.onBtnPlayClick()

		pass

	def onBtnBackClick(self):
		pass

	def onBtnPlayClick(self):
		print 'play click'
#		self.mediaObject.play()
		tis = self.tvToneList.selectedItems()
		if not tis:
			return
		ti = tis[0]
		digest = self.idxdata_archives[ti]
		self.playPrepare(digest)


	def tick(self, time):

		secs = time/1000
		secs2 = self.mediaObject.totalTime()/1000
		text = '%s/%s'%(utils.formatTimeLength(secs),utils.formatTimeLength(secs2))
		self.txtPlayIndicator.setText(text)

		# displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
		# self.timeLcd.display(displayTime.toString('mm:ss'))

	def resetPlayTime(self):
		self.txtPlayIndicator.setText('00:00:00/00:00:00')
		pass

	def stateChanged(self, newState, oldState):
		if newState == Phonon.ErrorState:
			if self.mediaObject.errorType() == Phonon.FatalError:
				QtGui.QMessageBox.warning(self, "Fatal Error",
						self.mediaObject.errorString())
			else:
				QtGui.QMessageBox.warning(self, "Error",
						self.mediaObject.errorString())

		elif newState == Phonon.PlayingState:
			self.btnPlay.setEnabled(False)
			self.btnPause.setEnabled(True)
			self.btnStop.setEnabled(True)

		elif newState == Phonon.StoppedState:
			self.btnStop.setEnabled(False)
			self.btnPlay.setEnabled(True)
			self.btnPause.setEnabled(False)
			self.resetPlayTime()
			self.mediaObject.stop()

		elif newState == Phonon.PausedState:
			self.btnPause.setEnabled(False)
			self.btnPlay.setEnabled(True)
			self.btnStop.setEnabled(True)

	def sourceChanged(self, source):
#		self.musicTable.selectRow(self.sources.index(source))
#		self.timeLcd.display('00:00')
		self.resetPlayTime()


	def metaStateChanged(self, newState, oldState):
		if newState == Phonon.ErrorState:
			QtGui.QMessageBox.warning(self, "Error opening files",
					self.metaInformationResolver.errorString())

			while self.sources and self.sources.pop() != self.metaInformationResolver.currentSource():
				pass

			return

		if newState != Phonon.StoppedState and newState != Phonon.PausedState:
			return

		if self.metaInformationResolver.currentSource().type() == Phonon.MediaSource.Invalid:
			return

		metaData = self.metaInformationResolver.metaData()

		title = metaData.get('TITLE', [''])[0]
		if not title:
			title = self.metaInformationResolver.currentSource().fileName()

		titleItem = QtGui.QTableWidgetItem(title)
		titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)

		artist = metaData.get('ARTIST', [''])[0]
		artistItem = QtGui.QTableWidgetItem(artist)
		artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)

		album = metaData.get('ALBUM', [''])[0]
		albumItem = QtGui.QTableWidgetItem(album)
		albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)

		year = metaData.get('DATE', [''])[0]
		yearItem = QtGui.QTableWidgetItem(year)
		yearItem.setFlags(yearItem.flags() ^ QtCore.Qt.ItemIsEditable)

		currentRow = self.musicTable.rowCount()
		self.musicTable.insertRow(currentRow)
		self.musicTable.setItem(currentRow, 0, titleItem)
		self.musicTable.setItem(currentRow, 1, artistItem)
		self.musicTable.setItem(currentRow, 2, albumItem)
		self.musicTable.setItem(currentRow, 3, yearItem)

		if not self.musicTable.selectedItems():
			self.musicTable.selectRow(0)
			self.mediaObject.setCurrentSource(self.metaInformationResolver.currentSource())

		index = self.sources.index(self.metaInformationResolver.currentSource()) + 1

		if len(self.sources) > index:
			self.metaInformationResolver.setCurrentSource(self.sources[index])
		else:
			self.musicTable.resizeColumnsToContents()
			if self.musicTable.columnWidth(0) > 300:
				self.musicTable.setColumnWidth(0, 300)

	def aboutToFinish(self):
		pass
#		index = self.sources.index(self.mediaObject.currentSource()) + 1
#		if len(self.sources) > index:
#			self.mediaObject.enqueue(self.sources[index])

	def setTermInfo(self,term):
#		print term.keys()
		print 'setTermInfo:', term
		if term['org']:
			self.txtOrganization.setText(term['org'])
		if term['phone']:
			self.edtPhone.setText( term['phone'])
		if term['employee']:
			self.edtEmployee.setText( term['employee'])
		if term['address']:
			self.edtAddress.setText(term['address'])
		if term['addition']:
			self.edtAddition.setText(term['addition'])

	def onTrayIconActived(self,reason):
#		print reason ,QSystemTrayIcon.DoubleClick
		if reason == QSystemTrayIcon.DoubleClick:
#			self.show()
			self.showNormal()
			self.activateWindow()
			self.raise_()


	# def mouseMoveEvent(self,event):
		# if getApp().timeLocked():
		# 	self.lockScreen()
		# print 'on mouseMoveEvent'


	def showEvent (self,event ):
		if getApp().isReachTimeLock():
			self.lockScreen()

	def _doExit(self):
		r = QMessageBox.question(self,u'提示',u'确认要退出语音终端程序?',QMessageBox.Yes|QMessageBox.No|QMessageBox.Warning,QMessageBox.No)
		if r != QMessageBox.Yes:
			return
		self.icontray.hide()
		getApp().running = False
		QtGui.qApp.closeAllWindows()
		usbcmd.UsbHost.instance().close()
		utils.killProcess(os.getpid())

	def onMenuExit(self):
		import form_lockscreen
		if form_lockscreen.FormLockScreen.handle:
			form_lockscreen.FormLockScreen.handle.close()
			
		r = QMessageBox.question(self,u'提示',u'确认要退出语音终端程序?',QMessageBox.Yes|QMessageBox.No|QMessageBox.Warning,QMessageBox.No)
		if r != QMessageBox.Yes:
			return
		self.icontray.hide()
		getApp().running = False
		QtGui.qApp.closeAllWindows()
		usbcmd.UsbHost.instance().close()
		utils.killProcess(os.getpid())
#		self.destroy()


	def onMenuLockScreen(self):
		passwd = getApp().getLockPasswd()
		if not passwd or passwd=='111111':
			QMessageBox.about(self,u'提示',u'锁屏密码未设置，锁屏功能无法启动!')
			return

		self.lockScreen()

	def onMenuLockScreenSettings(self):
		import form_lockscreen_settings
		form = form_lockscreen_settings.FormLockSettings()
		form.exec_()



	def onMenuConfig(self):
		self.showNormal()
		self.activateWindow()
		self.raise_()


	def onMenuAudioMgr(self):
		pass

	def exitApp(self,event):
		#return self.onMenuExit()
		import form_lockscreen
		print form_lockscreen.FormLockScreen.handle
		if form_lockscreen.FormLockScreen.handle:
			form_lockscreen.FormLockScreen.handle.close()

		return self._doExit()

# 		self.show()
# 		print 'x'*20
# 		r = QMessageBox.question(self,u'提示',u'确认要退出语音终端程序?',QMessageBox.Yes|QMessageBox.No|QMessageBox.Warning,QMessageBox.No)
#
# 		if r != QMessageBox.Yes:
# 			self.hide()
# 			return
#
# 		self.icon.hide()
# #		self.running = False
# 		getApp().running = False
# 		self.show()
# 		QtGui.qApp.closeAllWindows()
# 		self.destroy()




	def closeEvent(self,event):
#		print event
		if getApp().running:
			event.ignore()
			self.hide()
			#self.icon.setToolTip(u'语音软件最小化...')
			msg = getApp().getSystemConfig('tray_min_message','').decode('utf-8')
			self.icontray.showMessage(u'提示',msg)
		else:
			event.accept()
			# qApp.closeAllWindows()


	def work_thread(self):
		'''
		同步数据到服务器
		'''
		wait =getApp().getSystemConfig('thread_wait','5')
		wait = int(wait)
		getApp().init_db() # sqlite只能在一个线程中使用

		while getApp().running:
#			self.txtStatus.setText('not connected..')
			time.sleep(wait)
			try:
				print 'scanning...'
				filesync.scan()
				print 'done filesync'
#				continue

				# getApp().getLogger().getLogger().handlers[0].flush()
				if not getApp().running:
					break
				if not getApp().getToken():
					print 'try termLogin..'
					if not self.termLogin(): #注册终端
						continue
					print 'login okay!'
				if not getApp().getToken():
					continue

#				if not self.connToServer:   #socket 链接到服务器
#					if not self.connectToServer():
#						continue
#					m = message.MsgTermHeartBeat()
#					self.connToServer.sendMessage(m)

				# filesync.sync()             #同步本地spx文件到服务器
				filesync.sync_mp3()             #同步本地spx文件到服务器
				archive.syncToServer(getApp().getDB().handle())      #同步spx文件信息到服务器
				client.syncToServer(getApp().getDB().handle())
			except:
				traceback.print_exc()

		print 'workthread end..'
		# if self.connToServer:
		# 	self.connToServer.close()

	def getDiskFree(self):
	#计算磁盘空间
		user,all = utils.statevfs(getApp().getAudioStorePath())

		user = user/1024/1024/1024.
		all = all/1024/1024/1024.
		user = round(user,3)
		all = round(all,3)
		return all,user

	def onTimer(self):
		try:
			s = u'未注册'
			if getApp().getToken():
				s = u'已注册'
			# if self.connToServer:
			# 	s+=u',已连接'
			# else:
			# 	s+=u',未连接'

			self.txtStatus.setText(s)
			self.txtRegStatus.setText(s)

			user,all = self.getDiskFree()

			self.txtDiskResource.setText(u'总空间:%.3f G,已使用:%.3f G,可用:%.3f,使用率：%d%%'%(all,all-user,user,
			                                                                        (all-user)/all*100))
			self.setTrayIcon()

			#磁盘空间小或者未注册到服务器，显示报警状态
			if user < AppConst.MIN_DISK_FREESPACE or not getApp().getToken():
				self.setTrayIcon('alert')

			#usb未检测到显示灰色
			if not usbcmd.UsbHost.instance().current:
				self.setTrayIcon('disable')

			#锁屏功能
			if getApp().isReachTimeLock():
				if not getApp().timeLocked():
					self.lockScreen()

			#self.checkSoftwareVersion()
		except:
			traceback.print_exc()

	def checkSoftwareVersion(self):
		import urllib2
		if not hasattr(self,'_software_version_checked'):
			setattr(self,'_software_version_checked',False)

		if self._software_version_checked:
			return
		#
		try:
			server = getApp().getSettings().get('webserver')
			if server.find('http')==-1:
				server = 'http://'+server
			f = urllib2.urlopen('%s/WebApi/Terminal/getTermVersion'%(server),timeout=2)   # POST
			d = f.read()
			d = json.loads(d)
			if d['status'] != 0 :
				return False
			ver = d['result'] #返回软件最新版本号

			print 'software version:',ver
			if  ver and ver!=APP_VER:
				#QMessageBox.about(None,u'提示',u'系统终端软件新版本:%s 请及时更新!'%ver)
				#form_message.about(self,u'提示',u'系统终端软件新版本:%s 请及时更新!'%ver)
				form_message.about(self,u'提示',u'发现新版本(%s)语言终端管理软件,请在"状态"界面，点击"最新版本"按钮进行下载更新并安装!'%ver)
			self._software_version_checked = True
		except:
			traceback.print_exc()


	def lockScreen(self):

		import form_lockscreen
		self.setEnabled(False)
		getApp().timeLock()
		if self.isVisible():

			if form_lockscreen.FormLockScreen.handle:
				return
			print 'lock screen..'
			form = form_lockscreen.FormLockScreen(self)
			# r = form.exec_()
			form.show()
			# if not form.ok:
			# 	print 'cancel,but locking continue..'
				# self.hide()
		# print 'window be locked!'

	def unlockScreen(self):
		self.setEnabled(True)
		getApp().timeUnlock()
		self.show()
		self.raise_()
		print 'window be unlocked'

	def networkRecvEvent(self,evt):
		'''
			接收服务发送过来的消息
		'''
		if evt.type == network.NetConnectionEvent.EVENT_DATA:
			for m in evt.data:
				if m.getMsg() == 'imageput_selectnode_resp':
					pass #mtxobj.notify(m)

		if evt.type == network.NetConnectionEvent.EVENT_DISCONNECTED:
			getApp().getSettingsValue('lost connection with server')
			self.connToServer = None


	def connectToServer(self):
		try:
			conn = network.NetConnection(recvfunc = self.networkRecvEvent)
			server = getApp().getSettingsValue('commserver')
			getApp().getLogger().info('try connect commserver :'+server)
			address = utils.parseInetAddress(server)
			r = conn.connect( address )
			if not r:
				getApp().getLogger().info('server unreachable! address:' + server)
				return False
			thread = network.NetConnThread(conn)
			self.connToServer = conn
			#发送认证信息
			m = message.MsgTermRegister()
			m['token'] = getApp().getToken()
			self.connToServer.sendMessage(m)
		except:
			traceback.print_exc()
		return False

	def termLogin(self):

		try:
			user = getApp().getSettings().get('user')
			passwd = getApp().getSettings().get('passwd')
#			passwd = getApp().decryptValue(passwd)

			server = getApp().getSettings().get('webserver')
			if server.find('http')==-1:
				server = 'http://'+server
			getApp().getLogger().info('[termLogin] try register terminal..')


			params = urllib.urlencode({'user':user,'passwd':passwd,'appver':APP_VER})
			getApp().getLogger().info(server)
			# getApp().getLogger().info(unicode(params))

			f = urllib.urlopen('%s/WebApi/Terminal/login'%(server),params)   # POST
			d = f.read()
			d = json.loads(d)

			if d['status'] == 0:
				getApp().token = d['result']['token']
				self.showTermInfo(getApp().getToken())
				getApp().getLogger().info('login succ:'+getApp().getToken())
				return True

			getApp().getLogger().info('login reject:'+ str(d))
		except:
#			traceback.print_exc()
			getApp().getLogger().info('[termLogin] webapi call failed:%s'%server)
			return False

		return False



	def onBtnCheckVersionClick(self):
		'''
			直接打开浏览器转到 download/目录
		'''
		server = getApp().getSettings().get('webserver')
		if server.find('http')==-1:
			server = 'http://'+server
		url = '%s/download/'%server
		import webbrowser
		webbrowser.open(url)

	def onBtnLoginClick(self):
		'''
			测试连接
		'''
		try:
			user = self.edtUser.text().toUtf8().data().strip()
			passwd = self.edtPasswd.text().toUtf8().data().strip()

			server = self.edtServer1.text().toUtf8().data().strip().lower()
			server2 = self.edtServer2.text().toUtf8().data().strip().lower()

			if not user or not passwd or not server :
				QMessageBox.about(self,u'提示',u'测试输入项不能为空!')
				return
			#			server = 'http://'+server
			params = urllib.urlencode({'user':user,'passwd':passwd})
			if server.find('http')==-1:
				server = 'http://'+server
			f = urllib.urlopen('%s/WebApi/Terminal/login'%(server),params)   # POST
			d = f.read()
			d = json.loads(d)
			if d['status'] == 0 :
				token = d['result']['token']

				getApp().setSettingsValue('user',user)
				getApp().setSettingsValue('passwd',passwd)
				getApp().setSettingsValue('webserver',server)
				getApp().setSettingsValue('commserver',server2)
				getApp().saveSettings()
				#-- getTermInfo()
				self.showTermInfo(token)
				QMessageBox.about(self,u'提示',u'与服务成功建立连接!')
				return
		except:
			traceback.print_exc()
		QMessageBox.about(self,u'提示',u'服务器认证失败!')


	def showTermInfo(self,token):
		params = urllib.urlencode({'token':token})
		server = getApp().getSettingsValue('webserver')
		try:
#			self.txtOrganization.setText('')
#			self.edtPhone.setText('')
#			self.edtEmployee.setText('')
#			self.edtAddress.setText('')
#			self.edtAddition.setText('')

			if server.find('http')==-1:
				server = 'http://'+server

			f = urllib.urlopen('%s/WebApi/Terminal/getTermInfo'%(server),params)   # POST
			d = f.read()
			d = json.loads(d)
			if d['status'] == 0:
				rst = d['result']
				self.singal_SetTermInfo.emit(rst)
#				self.txtOrganization.setText(rst['ogr'].decode('utf-8'))
#				self.edtPhone.setText(rst['phone'].decode('utf-8'))
#				self.edtEmployee.setText(rst['employee'].decode('utf-8'))
#				self.edtAddress.setText(rst['address'].decode('utf-8'))
#				self.edtAddition.setText(rst['addition'].decode('utf-8'))

		except:
			traceback.print_exc()


	def _export_archives(self,filename):

		import xlwt

		try:
			wbk = xlwt.Workbook()
			sheet = wbk.add_sheet('sheet 1')
			#写表头
			fs =[]
			ti = self.tvToneList.headerItem()
			for col in range(ti.columnCount()):
				fs.append( ti.text(col).toUtf8().data().decode('utf-8') )
			c = 0
			for f in fs:
				sheet.write( 0,c,f)
				c+=1
			r = 1
			rows = self.idxdata_archives.keys()
			rows.sort(cmp=lambda x,y:cmp(  int(x.text(0).toUtf8().data()),
			                               int(y.text(0).toUtf8().data())
										) )

			for ti in rows:
				for col in range(ti.columnCount()):
					val =  ti.text(col).toUtf8().data().decode('utf-8')
					sheet.write(r,col,val )
				r+=1
			wbk.save(filename)
		except:
			traceback.print_exc()
			return False

		return True


	def onMenuItem_ArchiveExport(self):
		file = QFileDialog.getSaveFileName(self,u'选择导出文件','',u'通话记录(*.xls)')
		if not file:
			return
		#生成输出文件
		file = file.toUtf8().data().decode('utf-8')
		import client
		rc = self._export_archives(file)
		if not rc:
			QMessageBox.about(self,u'提示',u'导出失败!')
			return
		QMessageBox.about(self,u'提示',u'导出okay')


	def onMenuItem_ArchiveUnMatched(self):
		self.tvToneList.clear()
		self.idxdata_archives={}
		sql = "select a.* from core_audiofile a where client_sid=''  "

		start = self.dtToneStart.dateTime().toTime_t ()
		end = self.dtToneEnd.dateTime().toTime_t ()
		sql+=' and (filetime between %s and %s)'%(start,end)
		sql+=' order by filetime desc limit 500'
		cr = self.db.handle().cursor()
		cr.execute(sql)
		rs = fetchallDict(cr)
		idx = 0
		for r in rs:
			#----- 删除不存在的记录 --------
			if getApp().getSystemConfig('remove_unresolved_record','0') == '1':
				if not os.path.exists(r['spxfile'].decode('utf-8')):
					cr = self.db.handle().cursor()
					cr.execute('delete from core_audiofile where digest=?',(r['digest'],))
					self.db.handle().commit()
					continue
			#----- END --------

			idx+=1
			tonetime = utils.formatTimestamp_ymdhm(r['filetime'])
			phone = r['phone']
			attr = u'未知'
			if r['attr'] == 0 :
				attr=u'来电'
			elif r['attr'] == 1:
				attr=u'去电'
			elif r['attr'] == 2:
				attr=u'录音'
			elif r['attr'] == 3:
				attr = u'未接'
			duration = r['duration']
			duration = utils.formatTimeLength(duration)
			memo = r['memo'].replace('\n',' ')
			client = ''
			personid = ''
			clientid =''

			synced = u'未上传'
			if r['status']:
				synced = u'已上传'

			tonetype = AppConst.valueToStr(r['type'])
			productid = r['productid'].decode('utf-8')

			row = ('%02d '%idx,
					tonetime+' '*2,
					phone.decode('utf-8')+'  ',
			       client.decode('utf-8')+' ',
#			       personid.decode('utf-8'),
			       clientid.decode('utf-8')+' ',
			       attr,
#			       tonetype,
			       duration,
			       synced,
			       productid+' ',
			       memo.decode('utf-8')
				)
			ti = QTreeWidgetItem(row )
			self.tvToneList.addTopLevelItem(ti)
			self.idxdata_archives[ti] = r['digest']


		self.tvToneList.resizeColumnToContents(0)
		self.tvToneList.resizeColumnToContents(1)
		self.tvToneList.resizeColumnToContents(2)
		self.tvToneList.resizeColumnToContents(3)

	def onMenuItem_ArchiveUnMatchedMulti(self):
		self.tvToneList.clear()
		self.idxdata_archives={}

		cr = self.db.handle().cursor()
		sql = "select * from core_audiomapclient order by filetime desc"
		cr.execute(sql)
		rs = fetchallDict(cr)
		rs2=[]
		for r in rs:
			digest = r['digest']
			sql = "select a.* from core_audiofile a where 1=1 and digest=? "
			start = self.dtToneStart.dateTime().toTime_t ()
			end = self.dtToneEnd.dateTime().toTime_t ()
			sql+=' and (filetime between %s and %s)'%(start,end)
			cr.execute(sql,(r['digest'],))
			rs3 = fetchallDict(cr)

			for r3 in rs3:
				if r3['client_sid']:
					sql = 'delete from core_audiomapclient where digest=?'
					cr.execute(sql,(digest,))
					self.db.handle().commit()
					continue
				rs2.append(r3)
		rs = rs2
		idx = 0
		for r in rs:

			idx+=1
			tonetime = utils.formatTimestamp_ymdhm(r['filetime'])
			phone = r['phone']
			attr = u'未知'
			if r['attr'] == 0 :
				attr=u'来电'
			elif r['attr'] == 1:
				attr=u'去电'
			elif r['attr'] == 2:
				attr=u'录音'
			elif r['attr'] == 3:
				attr = u'未接'
			duration = r['duration']
			duration = utils.formatTimeLength(duration)
			memo = r['memo'].replace('\n',' ')
			client = ''
			personid = ''
			clientid =''


			if r['client_sid']:
				sql = 'select * from core_client where sid = ?'
				cr = self.db.handle().cursor()
				cr.execute(sql,(r['client_sid'],))
				clients = fetchallDict(cr)
				if clients:
					client = clients[0]['name']
					personid = clients[0]['personid']
					clientid = clients[0]['clientid']

			synced = u'未上传'
			if r['status']:
				synced = u'已上传'

			tonetype = AppConst.valueToStr(r['type'])
			productid = r['productid'].decode('utf-8')

			row = ('%02d '%idx,
					tonetime+' '*2,
					phone.decode('utf-8')+'  ',
			       client.decode('utf-8')+' ',
#			       personid.decode('utf-8'),
			       clientid.decode('utf-8')+' ',
			       attr,
#			       tonetype,
			       duration,
			       synced,
			       productid+' ',
			       memo.decode('utf-8')
				)
			ti = QTreeWidgetItem(row )
			self.tvToneList.addTopLevelItem(ti)
			self.idxdata_archives[ti] = r['digest']


		self.tvToneList.resizeColumnToContents(0)
		self.tvToneList.resizeColumnToContents(1)
		self.tvToneList.resizeColumnToContents(2)
		self.tvToneList.resizeColumnToContents(3)


	def onBtnAutoLoginClick(self):
		pass

	def onBtnSaveClick(self):
		#链接参数变化，则需要重新链接服务器
		user = self.edtUser.text().toUtf8().data().strip()
		passwd = self.edtPasswd.text().toUtf8().data().strip()
		server1 = self.edtServer1.text().toUtf8().data().strip()
		server2 = self.edtServer2.text().toUtf8().data().strip()

		phone = self.edtPhone.text().toUtf8().data().strip()
		employee = self.edtEmployee.text().toUtf8().data().strip()
		address = self.edtAddress.text().toUtf8().data().strip()
		addition = self.edtAddition.toPlainText ().toUtf8().data().strip()
		phonepasswd = self.edtPhonePasswd.text().toUtf8().data().strip()
		if not phonepasswd:
			phonepasswd='0000'
		try:

			if user!= getApp().getSettings().get('user') or \
				passwd!=getApp().getSettings().get('passwd') or \
				server1 != getApp().getSettings().get('webserver'):
				getApp().token = '' #需要重新认证了
				self.edtPhone.clear()
				self.edtEmployee.clear()
				self.edtAddress.clear()
				self.edtAddition.clear()
				self.txtOrganization.clear()

			# if server2 != getApp().getSettings().get('commserver'):
			# 	self.destroyServerConnection()

			# getApp().setSettingsValue('phone',phone)
			# getApp().setSettingsValue('employee',employee)
			# getApp().setSettingsValue('address',address)
			# getApp().setSettingsValue('addition',addition)
			getApp().setSettingsValue('phone_passwd',phonepasswd)
			getApp().saveSettings()
			
			# self.updateTermInfo()
		except:
			traceback.print_exc()
		finally:
			getApp().setSettingsValue('user',user)
			getApp().setSettingsValue('passwd',passwd)
			getApp().setSettingsValue('webserver',server1)
			getApp().setSettingsValue('commserver',server2)

			# getApp().setSettingsValue('phone',phone)
			# getApp().setSettingsValue('employee',employee)
			# getApp().setSettingsValue('address',address)
			# getApp().setSettingsValue('addition',addition)
			getApp().setSettingsValue('phone_passwd',phonepasswd)

			getApp().saveSettings()

			QMessageBox.about(self,u'提示',u'参数配置已保存!')

	def updateTermInfo(self):
		rc = False
		try:
			phone = self.edtPhone.text().toUtf8().data().strip()
			employee = self.edtEmployee.text().toUtf8().data().strip()
			address = self.edtAddress.text().toUtf8().data().strip()
			addition = self.edtAddition.toPlainText ().toUtf8().data().strip()

			server = getApp().getSettings().get('webserver')

			params = urllib.urlencode({'token':getApp().getToken(),
			                           'phone':phone,
			                           'employee':employee,
			                           'address':address,
			                           'addition':addition})

			if server.find('http')==-1:
				server = 'http://'+server

			f = urllib.urlopen('%s/WebApi/Terminal/updateTermInfo'%(server),params)   # POST
			d = f.read()
			d = json.loads(d)
			if d['status'] == 0:
				rc =  True
		except:
			traceback.print_exc()
			rc = False
		if not rc:
			QMessageBox.warning(self,u'提示',u'修改终端信息失败!')
		else:
			QMessageBox.warning(self,u'提示',u'操作成功!')

	def destroyServerConnection(self):
		try:
			self.connToServer.close()
			self.connToServer = None
		except:
			pass
		pass

	def onBtnAutoStartWithOsStartClick(self):
		run = False
		if self.ckAutoStartWithOsStart.checkState():
			run = True
		path = getApp().getBinPath()+'/main.exe'
		path = os.path.normpath(path)
		path = unicode(path)
		utils.setAutoRunWithOsStart(AppConst.APP_NAME_AUTORUN,path,run)


	def onPhoneIncoming(self,number):
		'''
			电话振铃
		'''
		form_tone_ring.FormToneRing.instance().showIncomingCall(number)


	def onPhoneNewSerial(self,number,attr,serial):
		'''
			number - 电话
			attr - 来电、去电、其他
			serial - 录音文件序号

			此信号到达不能知道是呼入还呼出， 去电时会即刻收到此消息，如果关闭电话提示窗口就不大好了
		'''
		form_tone_ring.FormToneRing.instance().onPhoneNewSerial(number,attr,serial)
		return

		#if attr not in (0,1):
		#	number=''
		#note={'spx_index':int(serial),
		#      'calltype':int(attr),
		#      'phone':number,
		#      'duration':0
		#}
		#form_tone_ring.FormToneRing.instance().close()  #接听则关闭来电提示窗口
		#changable = False
		#if int(attr) == 1: #呼出
		#	changable = True
		#
		#form_audio_note.FormAudioNote.instance().showNote(note,changable)


	def onPhoneHangOn(self):
		'''
			电话摘机
		'''
		pass


	def onPhoneRingEnd(self):
		'''
			振铃未接，收到挂断消息则关闭来电提示窗口
		'''
		print 'phone ringing end..'
		if form_tone_ring.FormToneRing.handle:
			form_tone_ring.FormToneRing.instance().close()

	def onPhoneHangUp(self):
		'''
			话机挂断
		'''
		if form_tone_ring.FormToneRing.handle:
			form_tone_ring.FormToneRing.instance().close()
		form_audio_note.currrent_dial_out_csid =''


	def onPhoneDial(self,number):
		'''
			话机主动拨号，这里不做处理
			话机端无法实现获知完整的拨号号码
		'''
		import form_tone_ring   #2013.11.9
		import form_audio_note
		if  form_audio_note.FormAudioNote.handle:
			form_audio_note.FormAudioNote.instance().phoneKeyPress(number)

		if form_tone_ring.FormToneRing.handle:
			form_tone_ring.FormToneRing.instance().phoneKeyPress(number)



	def winEvent(self,msg):

		if msg.message == win32con.WM_MOUSEMOVE:
			# print 'mouse move ..'
			if not getApp().timeLocked():
				getApp().timeUnlock()


			# print 'mouse move'




		if msg.message == win32con.WM_COPYDATA:
			print msg.wParam,msg.lParam
			pCDS = ctypes.cast(msg.lParam, PCOPYDATASTRUCT)
#			print pCDS.contents.dwData
#			print pCDS.contents.cbData

			#电话打入
			if msg.wParam == AppConst.PHONE_INCOMING:
				print 'PHONE_INCOMING'
				number = ctypes.string_at(pCDS.contents.lpData)
				self.onPhoneIncoming(number)
			#开始录音
			elif msg.wParam == AppConst.PHONE_RECORDING:
				s = ctypes.string_at(pCDS.contents.lpData)
				number,attr,serial = s.split(',')
				self.onPhoneNewSerial(number,attr,serial)
			#挂机
			elif msg.wParam == AppConst.PHONE_HANGUP:
				pass

			#通话接通
			elif msg.wParam == AppConst.PHONE_HANGON:
				pass

#			print ctypes.string_at(pCDS.contents.lpData)

		return False,0


if __name__=='__main__':
	pass