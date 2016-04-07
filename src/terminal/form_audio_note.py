# -*- coding: utf-8 -*-


from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,time,datetime,traceback,string,json,pickle,os,os.path
from  ui_audio_note import *
import utils
from base import *
import dbsql
from dbconn import *

import form_select_client

FILE_TEMP_OPERATORS = 'operators.tmp'

current_audio = ''

currrent_dial_out_csid='' #当前外拨电话的客户编号

class FormAudioNote(QtGui.QFrame,Ui_FrameArchiveNote):
	CALLIN = 0
	CALLOUT = 1
	HISTORY = 2    #录音编辑,此时将不接收按键消息

	handle = None
	def __init__(self,parent=None):
		# QtGui.QFrame.__init__(self,parent)
		QtGui.QFrame.__init__(self,None)
		self.setupUi(self)
		self.db = dbsql.SqlPrepare()
		self.connect(self.btnSave,SIGNAL('clicked()'),self.onBtnSaveClick)
		self.connect(self.btnClose,SIGNAL('clicked()'),self.onBtnCloseClick)
		self.connect(self.btnSelectClient,SIGNAL('clicked()'),self.onBtnSelectClientClick)

		keys = AppConst.tone_types.keys()
		keys.sort()
		for k in keys:
			self.cbxToneType.addItem(AppConst.valueToStr(k),k)


		#self.cbxToneType.addItem(AppConst.valueToStr(AppConst.ARCHIVE_NOTE_TYPE_NORMAL),AppConst.ARCHIVE_NOTE_TYPE_NORMAL)
		#self.cbxToneType.addItem(AppConst.valueToStr(AppConst.ARCHIVE_NOTE_TYPE_SALE),AppConst.ARCHIVE_NOTE_TYPE_SALE)
		#self.cbxToneType.addItem(AppConst.valueToStr(AppConst.ARCHIVE_NOTE_TYPE_OTHER),AppConst.ARCHIVE_NOTE_TYPE_OTHER)
		self.edtClientName.setVisible(False)
		self.edtPhone.setEnabled(False)
		
		self.setWindowFlags( Qt.Dialog )

		self.show()
		self.note={}
#		self.raise_()
		self.client_sid=''
		self.allow_change =False#

		font = QtGui.QFont(AppConst.APP_FONT_NAME,10)
		self.setFont(font)

		self.timer = QTimer()
		self.connect(self.timer,SIGNAL('timeout()'),self.onTimer)
		self.duration = 0

		self.operators = utils.loadValuesFromFile(FILE_TEMP_OPERATORS)
		for opt in self.operators:
			self.cbxCurrOperator.addItem(opt.decode('utf-8'))

		self.cbxCurrOperator.lineEdit().setMaxLength(30)
		self.cbxClientNames.lineEdit().setMaxLength(30)

	@staticmethod
	def instance(parent=None):
		if not FormAudioNote.handle:
			FormAudioNote.handle = FormAudioNote(parent)
		return FormAudioNote.handle

	def onTimer(self):
		self.duration+=1
		self.edtToneTime.setText(utils.formatTimeLength( self.duration))

#	def saveIntoDb(self):
	def onBtnSaveClick(self):
		global  current_audio

		digest = self.note.get('spx_digest')
		index = self.note.get('spx_index')
		db = self.db.handle()
		try:
			#find client record by client-name
			# name = self.edtClientName.text().toUtf8().data().strip()
			name = self.cbxClientNames.currentText().toUtf8().data().strip()

			client=None
			phone = self.edtPhone.text().toUtf8().data().strip()
			memo = self.edtToneMemo.toPlainText().toUtf8().data().strip()


			type = self.cbxToneType.itemData(self.cbxToneType.currentIndex()).toInt()[0]
			productid = self.edtProductId.text().toUtf8().data().strip()
			#操作经理名称选择,保存
			operator = self.cbxCurrOperator.currentText().toUtf8().data().strip()
			if operator and self.operators.count(operator) == 0:
				self.operators.append(operator)
				utils.saveValuesToFile(FILE_TEMP_OPERATORS,self.operators)

			sid='' #客户编号 sid
			if name:
				if self.cbxClientNames.currentIndex()!=-1:
					list = self.cbxClientNames.itemData(self.cbxClientNames.currentIndex()).toStringList()
					if name == list[1]:
						sid = list[0].toUtf8().data()
					print 'xx'*20,repr(sid),repr(name)
					#sid = self.cbxClientNames.itemData(self.cbxClientNames.currentIndex()).toString().toUtf8().data()
				# print 'cur sid:',repr(sid)
				cr = db.cursor()
				if not sid:
					sql =" select * from core_client where name=? and memo!='%s' "%AppConst.CLIENT_DELETED_MARKER
					cr.execute(sql,(name,))
					rs = fetchallDict(cr)
					# print '---',repr(rs)
					if rs:
						r = rs[0]
						client = r
						sid = r['sid']
						sql=''  #电话为空，自动填入某一个
						if not r['phone1'].strip():
							sql = 'update core_client set phone1=?,status=0 where sid=?'
						elif not r['phone2'].strip():
							sql = 'update core_client set phone2=?,status=0 where sid=?'
						elif not r['phone3'].strip():
							sql = 'update core_client set phone3=?,status=0 where sid=?'
						# print sql
						# print sid,repr(phone)
						if sql and  phone:
							msg =u'电话号码将自动添加到客户:【%s】，\n是否要继续?'%name.decode('utf-8')
							r = QMessageBox.question(self,u'提示',msg,QMessageBox.Yes|QMessageBox.No|QMessageBox.Warning,
							                         QMessageBox.No)
							if r != QMessageBox.Yes:
								return
							cr = db.cursor()
							cr.execute(sql,(phone,sid))

					else: #找不到输入名称的客户记录则自动添加客户进去，并将电话号码写入phone1
						msg =u'指定客户:【%s】 不存在，系统将自动创建此客户记录。\n是否要继续?'%name.decode('utf-8')
						r = QMessageBox.question(self,u'提示',msg,QMessageBox.Yes|QMessageBox.No|QMessageBox.Warning,
						                         QMessageBox.No)
						if r != QMessageBox.Yes:
							return

						sid = dbsql.gen_sid()
						sql = "insert into core_client values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
						cr = db.cursor()
						pinyin = utils.multi_get_letter(name)
						cr.execute(sql,(sid,name,0,'',phone,
						                '','','','', #email
										'','','',
										'', # personid
										'',  # client-id
						                pinyin,
						                0,      # status as unuploaded,
						                '', #phone3
						                '', #owner_org
						                0 ,  #client type
						                ''  # custom_tag 2013.11.8
						))

			if digest: # 保存memo 到audiofile 记录
				cr = db.cursor()
				#--
				sql ="select count(*) as cnt from core_audiofile where phone=? and client_sid!='' and client_sid!=?"
				cr.execute(sql,(phone,sid))
				r = fetchoneDict(cr)
				if r['cnt'] == 0: #更新所有指定phone的记录的client_sid为当前客户sid
					sql='update core_audiofile set client_sid=?,memo_status=0 where phone=?'
					cr.execute(sql,(sid,phone))

				sql='update core_audiofile set client_sid=?,memo=?,memo_status=0,type=?,productid=?,operator=? where digest=?'
				cr.execute(sql,(sid,memo,type,productid,operator,digest))
				sql = 'delete from core_audiomapclient where digest=?'
				cr.execute(sql,(digest,))

			#-----------------------------------------------
			#来电备注填写
			if index!=None:
				#1.从audiofile找一下 对应的serial==index 是否存在
				cr = db.cursor()
				sql = 'select * from core_audiofile where serial=?'
				cr.execute(sql,(index,))
				rs = fetchallDict(cr)
				print '8-'*20
				if rs:
					digest = rs[0]['digest']
					sql ="select count(*) as cnt from core_audiofile where phone=? and client_sid!='' and client_sid!=?"
					cr.execute(sql,(phone,sid))
					r = fetchoneDict(cr)
					if r['cnt'] == 0: #更新所有指定phone的记录的client_sid为当前客户sid
						sql='update core_audiofile set client_sid=?,memo_status=0 where phone=?'
						cr.execute(sql,(sid,phone))

					sql = 'delete from core_audiomapclient where digest=?'
					cr.execute(sql,(digest,))

					sql='update core_audiofile set memo_status=0,memo=?,client_sid=?,type=?,productid=? where serial=?'
					cr.execute(sql,(memo,sid,type,productid,index))
				else: #不存在spx文件记录则将界面填写数据写入audiotemp内
					# 2014.1.3 合并多条缓冲记录
					sql = 'select count(*) as num from core_audiotemp where serial=? '
					cr.execute(sql,(index,))
					r = fetchoneDict(cr)
					if r['num'] == 0:
						sql='insert into core_audiotemp values(?,?,?,?,?,?)'
						cr.execute(sql,(index,sid,memo,type,productid,operator))
					else:
						sql='update core_audiotemp set client_sid=?,memo=?,type=?,productid=?,operator=? where serial=?'
						cr.execute(sql,(sid,memo,type,productid,operator,index))

#					print 'insert core_audiotemp:',index,sid,memo,type,productid


			db.commit()
			if digest:
				getApp().mainwindow.onArchiveNoteEdit(digest) #编辑之后回调到记录列表刷新
			self.close()

		except:
			traceback.print_exc()
			db.rollback()


	def onBtnCloseClick(self):
		self.close()

	def cb_get_client(self,sid,name):
		print sid,name
		#self.edtClientName.setText(name.decode('utf-8'))
		self.cbxClientNames.setEditText(name.decode('utf-8'))


	def onBtnSelectClientClick(self):

		form = form_select_client.FormSelectClient.instance()
		form.select(self.cb_get_client)

		pass

	def phoneKeyPress(self,number):
		if not self.allow_change:
			return  #不允许改电话号码
		if not number:
			return

		cr = self.db.handle().cursor()
		phone = number
		self.cbxClientNames.clearEditText()
		self.cbxClientNames.clear()
		self.edtPhone.setText(number.decode('utf-8'))
		sql = "select * from core_client where (phone1 = ? " \
			      "or phone2 =? or phone3 =?) and memo!='%s'"%AppConst.CLIENT_DELETED_MARKER
		cr.execute(sql,(phone,phone,phone))
		rs = fetchallDict(cr)
		for r in rs:
			value = '%s,~,%s'%(r['sid'],r['name'])
			value = QStringList()
			value.append(r['sid'])
			value.append(r['name'])
			self.cbxClientNames.addItem(r['name'].decode('utf-8'),value)
		if rs:
			self.cbxClientNames.setCurrentIndex(0)

	def showNote(self,note,allow_change_phone= False):
		'''
			note: {
				spx_digest, spx文件摘要
				spx_index,  录音文件索引号
				calltype,   电话呼叫类型
				phone,      电话号码
				duration,   时长
			}
		'''
		if self.timer.isActive():
			self.timer.stop()
			self.duration = 0
		# print '--'*20
		# print repr(note)
		self.show()
		self.raise_()
		self.allow_change = allow_change_phone
		self.cbxClientNames.setCurrentIndex(-1)
		self.cbxClientNames.clearEditText()
		self.cbxClientNames.clear()
		self.edtHistoryToneMemoList.clear()

		self.note = note
		cr = self.db.handle().cursor()
		sql=''
		digest = note.get('spx_digest')

		index = note.get('spx_index')
		calltype = note.get('calltype',0) #默认来电
		phone = note.get('phone','')
		duration = note.get('duration',0)
		if digest:  #录音文件已存在
			sql = 'select * from core_audiofile where digest=?'
			cr.execute(sql,(digest,))
			rs = fetchallDict(cr)
			if rs:
				r = rs[0]
				self.edtPhone.setText(r['phone'].decode('utf-8'))
				attr = u'未知'
				if r['attr'] == 0 :
					attr=u'来电'
				elif r['attr'] == 1:
					attr=u'去电'
				elif r['attr'] == 2:
					attr=u'录音'
				elif r['attr'] == 3:
					attr = u'未接'
				self.edtToneAttr.setText(attr)
				self.edtToneTime.setText(utils.formatTimeLength(r['duration']))
				self.edtToneMemo.setText(r['memo'].decode('utf-8'))

				for n in range(self.cbxToneType.count()):
					attr = self.cbxToneType.itemData(n).toInt()[0]
					try:
						r['type'] = int(r['type'])
					except: r['type'] = 1

					if attr == int(r['type']):
						self.cbxToneType.setCurrentIndex(n)
						break

				self.edtProductId.setText(r['productid'].decode('utf-8'))
				sid = r['client_sid']
				print 'current archive: client_sid=',sid,r['phone']
				self.loadClientHistoryMemo(sid) #2013.11.9
				# if sid:
				# 	sql = 'select * from core_client where sid=?'
				# 	cr.execute(sql,(sid,))
				# 	rs = fetchallDict(cr)
				# 	if rs:
				# 		name = rs[0]['name']
				# 		#self.edtClientName.setText(name.decode('utf-8'))
				# 		self.cbxClientNames.setEditText(name.decode('utf-8'))
				phone = r['phone']
				rr = r
				if not phone:
					phone='z*'*20
				sql = "select * from core_client where (phone1 = ? " \
			      "or phone2 =? or phone3 =?) and memo!='%s'"%AppConst.CLIENT_DELETED_MARKER
				cr.execute(sql,(phone,phone,phone))
				rs = fetchallDict(cr)
				n = 0
				idx = -1
				for r in rs:
					value = QStringList()
					value.append(r['sid'])
					value.append(r['name'])
					#value = '%s,~,%s'%(r['sid'],r['name'])
					self.cbxClientNames.addItem(r['name'].decode('utf-8'),value)

					if r['sid'] == sid:
						idx = n

					n+=1
				self.cbxClientNames.setCurrentIndex(idx)
				r = rr
				self.cbxCurrOperator.setEditText( utils.normalizeString(r['operator']).decode('utf-8'))

		if index!=None:
			#通话状态，显示通话时间流逝
			self.edtToneTime.setText(utils.formatTimeLength(0))
			self.timer.start(1000*1)

			attr = u'未知'
			if calltype == 0 :
				attr=u'来电'
			elif calltype == 1:
				attr=u'去电'
			elif calltype == 2:
				attr=u'录音'
			elif calltype == 3:
				attr = u'未接'
			self.edtToneAttr.setText(attr)
			self.edtToneTime.setText(utils.formatTimeLength(duration))
			self.edtToneMemo.setText('')
			self.edtPhone.setText(phone.decode('utf-8'))
			self.edtProductId.setText('')

			#根据电话号码匹配客户名称
			if not phone:
				phone='z*'*20

			# sql = "select * from core_client where phone1 like '%%%s%%' " \
			#       "or phone2 like '%%%s%%' or phone3 like '%%%s%%' "%(phone,phone,phone)
			sql = "select * from core_client where (phone1 = ? " \
			      "or phone2 =? or phone3 =?) and memo!='%s'"%AppConst.CLIENT_DELETED_MARKER
			cr.execute(sql,(phone,phone,phone))
			rs = fetchallDict(cr)
			idx = -1
			n = -1
			for r in rs:
				n+=1
				value = QStringList()
				value.append(r['sid'])
				value.append(r['name'])
				#value = '%s,~,%s'%(r['sid'],r['name'])
				self.cbxClientNames.addItem(r['name'].decode('utf-8'),value)
				if currrent_dial_out_csid == r['sid']:
					idx = n
			if rs:
				if idx == -1:
					idx = 0
				self.cbxClientNames.setCurrentIndex(idx)
			#2013.11.8
			#print rs
			self.edtHistoryToneMemoList.clear()
			for r in rs:
				self.loadClientHistoryMemo(r['sid'],False)

			#--2014.1.3
			self._loadCachedArchiveNoteInfo(index)

	def _loadCachedArchiveNoteInfo(self,index):
		'''
			#2014.1.3
		'''
		cr = self.db.handle().cursor()
		sql = "select * from core_audiotemp where serial=?"
		cr.execute(sql,(index,))
		rs = fetchallDict(cr)
		if rs:
			r = rs[0]
			self.edtToneMemo.setText(r['memo'].decode('utf-8')) # 录音文件未产生之前，临时记录的备注信息
			self.edtProductId.setText(r['productid'].decode('utf-8'))
			self.cbxCurrOperator.setEditText( utils.normalizeString(r['operator']).decode('utf-8'))
			for n in range(self.cbxToneType.count()):
				attr = self.cbxToneType.itemData(n).toInt()[0]
				try:
					r['type'] = int(r['type'])
				except: r['type'] = 1

				if attr == int(r['type']):
					self.cbxToneType.setCurrentIndex(n)
					break


	# 2013.11.9
	def loadClientHistoryMemo(self,client_sid,clear=True):
		print '>>loadClientHistoryMemo:', client_sid
		if not client_sid:
			return
		if clear:
			self.edtHistoryToneMemoList.clear()

		cr = self.db.handle().cursor()
		sql = 'select * from core_audiofile where client_sid=? order by filetime desc limit 10'
		cr.execute(sql,(client_sid,))
		rs = fetchallDict(cr)
		for r in rs:
			text='%s %s\n'%(utils.formatTimestamp(r['filetime']),r['memo'])
			text = text.decode('utf-8')
			if r['memo']:
				self.edtHistoryToneMemoList.append( text )
		self.edtHistoryToneMemoList.verticalScrollBar().setSliderPosition(0) #2013.12.8


	def closeEvent(self, event ):
		FormAudioNote.handle = None
		global currrent_dial_out_csid
		currrent_dial_out_csid = ''

if __name__=='__main__':
	pass