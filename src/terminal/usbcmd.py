# -- coding:utf-8 --

import traceback,os,os.path,sys,time,ctypes,datetime,base64,hashlib
import pickle,win32api,win32con,win32ui
import struct
import format
import utils

import ctypes
from ctypes import *



_lib = None



_int_types = (c_int16, c_int32)
if hasattr(ctypes, 'c_int64'):
	# Some builds of ctypes apparently do not have c_int64
	# defined; it's a pretty good bet that these builds do not
	# have 64-bit pointers.
	_int_types += (ctypes.c_int64,)
for t in _int_types:
	if sizeof(t) == sizeof(c_size_t):
		c_ptrdiff_t = t

class c_void(Structure):
	# c_void_p is a buggy return type, converting to int, so
	# POINTER(None) == c_void_p is actually written as
	# POINTER(c_void), so it can be treated as a real pointer.
	_fields_ = [('dummy', c_int)]




_lib = None
errmsg= ''

#--------------------------------------------------------------

_lib = windll.LoadLibrary('SiUSBXp.dll')

SI_GetNumDevices = _lib.SI_GetNumDevices
SI_GetNumDevices.restype = c_int
SI_GetNumDevices.argtypes = (POINTER(c_int),)

SI_GetProductString = _lib.SI_GetProductString
SI_GetProductString.restype = c_int
SI_GetProductString.argtypes = (c_int,c_char_p,c_int)


SI_Open = _lib.SI_Open
SI_Open.restype = c_int
SI_Open.argtypes = (c_uint,POINTER(c_uint))


SI_Close = _lib.SI_Close
SI_Close.restype = c_int
SI_Close.argtypes = (c_uint,)

SI_Read = _lib.SI_Read
SI_Read.restype = c_int
SI_Read.argtypes = (c_uint,c_char_p,c_uint,POINTER(c_uint),c_uint)

SI_Write = _lib.SI_Write
SI_Write.restype = c_int
SI_Write.argtypes = (c_uint,c_char_p,c_uint,POINTER(c_uint),c_uint)


SI_FlushBuffers = _lib.SI_FlushBuffers
SI_FlushBuffers.restype = c_int
SI_FlushBuffers.argtypes = (c_uint,c_ubyte,c_ubyte)


SI_SetTimeouts = _lib.SI_SetTimeouts
SI_SetTimeouts.restype = c_int
SI_SetTimeouts.argtypes = (c_uint,c_uint)

SI_GetTimeouts = _lib.SI_GetTimeouts
SI_GetTimeouts.restype = c_int
SI_GetTimeouts.argtypes = (POINTER(c_uint),POINTER(c_uint) )



SI_CheckRXQueue = _lib.SI_CheckRXQueue
SI_CheckRXQueue.restype = c_int
SI_CheckRXQueue.argtypes = (c_uint,POINTER(c_uint),POINTER(c_uint) )







#// Return codes
SI_SUCCESS	=0x00
SI_DEVICE_NOT_FOUND	=   0xFF
SI_INVALID_HANDLE	=		0x01
SI_READ_ERROR		=		0x02
SI_RX_QUEUE_NOT_READY	=	0x03
SI_WRITE_ERROR			=	0x04
SI_RESET_ERROR			=	0x05
SI_INVALID_PARAMETER	=	0x06
SI_INVALID_REQUEST_LENGTH=	0x07
SI_DEVICE_IO_FAILED		=	0x08
SI_INVALID_BAUDRATE		=	0x09
SI_FUNCTION_NOT_SUPPORTED=	0x0a
SI_GLOBAL_DATA_ERROR	=	0x0b
SI_SYSTEM_ERROR_CODE	=	0x0c
SI_READ_TIMED_OUT		=	0x0d
SI_WRITE_TIMED_OUT		=	0x0e
SI_IO_PENDING			=	0x0f

#// GetProductString() function flags
SI_RETURN_SERIAL_NUMBER	=	0x00
SI_RETURN_DESCRIPTION	=	0x01
SI_RETURN_LINK_NAME		=	0x02
SI_RETURN_VID			=	0x03
SI_RETURN_PID			=	0x04

# // RX Queue status flags
SI_RX_NO_OVERRUN		=	0x00
SI_RX_EMPTY				=	0x00
SI_RX_OVERRUN			=	0x01
SI_RX_READY				=	0x02

# // Buffer size limits
SI_MAX_DEVICE_STRLEN	=	256
SI_MAX_READ_SIZE		=	4096*16
SI_MAX_WRITE_SIZE		=	4096

# // Type definitions
# typedef		int		SI_STATUS;
# typedef		char	SI_DEVICE_STRING[SI_MAX_DEVICE_STRLEN];

# // Input and Output pin Characteristics
SI_HELD_INACTIVE		=	0x00
SI_HELD_ACTIVE			=	0x01
SI_FIRMWARE_CONTROLLED	=	0x02
SI_RECEIVE_FLOW_CONTROL	=	0x02
SI_TRANSMIT_ACTIVE_SIGNAL=	0x03
SI_STATUS_INPUT			=	0x00
SI_HANDSHAKE_LINE		=	0x01

# // Mask and Latch value bit definitions
SI_GPIO_0				=	0x01
SI_GPIO_1				=	0x02
SI_GPIO_2				=	0x04
SI_GPIO_3				=	0x08

# // GetDeviceVersion() return codes
SI_CP2101_VERSION		=	0x01
SI_CP2102_VERSION		=	0x02
SI_CP2103_VERSION		=	0x03


currentDevice = None

import threading


def normarlize_phonenum(number):
	r = ''
	for c in number:
		if ord(c) == 0x0f:
			break
		if ord(c) == 0x0a:
			r+='*'
		elif ord(c) == 0x0b:
			r+='#'
		else:
			r+=str(ord(c))
	return r


class UsbMessage:
	GetFileNumber_1 = 0x01
	GetFileNumber_2 = GetFileNumber_1

	GetPasswd =    0x04
	GetSerialNumber = 0x05
	GetUserCode = 0x06
	SetUserCode = 0x07
	GetPhoneState = 0x08
	PhoneDial    = 0x09

	OnRing = 0x0b        #振铃
	OnHangOn = 1      #摘机
	OnHangUp = 2       #挂机
	OnNewSerial = 0x0c   #新录音文件号

	CMD = 0
	def __init__(self):
		self.cmd = self.CMD
		self.attrs={}

	# @classmethod
	def parse(cls,cmd,msg):
		return None

	def marshall(self):
		return ''

class UsbMsg1_GetFileNumber(UsbMessage):
	CMD  =0x01
	def __init__(self):
		UsbMessage.__init__(self)

	def marshall(self):
		return struct.pack('<BH',self.cmd,0)

class UsbMsg2_GetFileNumber(UsbMessage):
	CMD  =0x01
	def __init__(self):
		UsbMessage.__init__(self)
		self.value = 0

	def unmarshall(self,d):
		if len(d)<2:
			return False
		self.value, = struct.unpack('<H',d[:2])
		return True

class UsbMsg1_GetFileInfo(UsbMessage):
	CMD  =0x02
	def __init__(self):
		UsbMessage.__init__(self)
		self.value = 0  #

	def marshall(self):
		return struct.pack('<BHH',self.cmd,2,self.value)

class UsbMsg2_GetFileInfo(UsbMessage):
	CMD  =0x02
	def __init__(self):
		UsbMessage.__init__(self)
		self.value=''

	def unmarshall(self,d):
		if len(d)!=32:
			return False
		self.value = d
		return True

class UsbMsg1_GetFileContent(UsbMessage):
	CMD  =0x03
	def __init__(self):
		UsbMessage.__init__(self)
		self.address = 0    #read start offset of file
		self.blocksize = 512

	def marshall(self):
		return struct.pack('<BHIH',self.cmd,6,self.address,self.blocksize)

class UsbMsg2_GetFileContent(UsbMessage):
	CMD  =0x03
	def __init__(self):
		UsbMessage.__init__(self)
		self.value=''

	def unmarshall(self,d):
		self.value = d
		return True

class UsbMsg1_GetPassword(UsbMessage):
	CMD  =0x04
	def __init__(self):
		UsbMessage.__init__(self)

	def marshall(self):
		return struct.pack('<BH',self.cmd,0)

class UsbMsg2_GetPassowrd(UsbMessage):
	CMD  =0x04
	def __init__(self):
		UsbMessage.__init__(self)
		self.value=''

	def unmarshall(self,d):
		# print repr(d)
		for c in d:
			self.value+= str(ord(c))
		return True


class UsbMsg1_GetSerialNumber(UsbMessage):
	CMD  =0x05
	def __init__(self):
		UsbMessage.__init__(self)

	def marshall(self):
		return struct.pack('<BH',self.cmd,0)

class UsbMsg2_GetSerialNumber(UsbMessage):
	CMD  =0x05
	def __init__(self):
		UsbMessage.__init__(self)
		self.value=0


	def unmarshall(self,d):
		self.value,= struct.unpack('<I',d[:4])

		return True

class UsbMsg2_PhoneDial(UsbMessage):
	'''
		话机拨号，通知pc
	'''
	CMD  =0x0a
	def __init__(self):
		UsbMessage.__init__(self)
		self.number = ''


	def unmarshall(self,d):
		# self.number = struct.unpack('<20s',d[20])
		self.number = normarlize_phonenum(d)
		return True

class UsbMsg1_GetUserCode(UsbMessage):
	CMD  =0x06
	def __init__(self):
		UsbMessage.__init__(self)

	def marshall(self):
		return struct.pack('<BH',self.cmd,0)

class UsbMsg2_GetUserCode(UsbMessage):
	CMD  =0x06
	def __init__(self):
		UsbMessage.__init__(self)
		self.value=''

	def unmarshall(self,d):
		self.value, = struct.unpack('<I',d[:4])
		return True



class UsbMsg1_SetUserCode(UsbMessage):
	CMD  =0x07
	def __init__(self):
		UsbMessage.__init__(self)
		self.value = 0

	def marshall(self):
		return struct.pack('<BHI',self.cmd,4,self.value)


class UsbMsg1_GetPhoneState(UsbMessage):
	CMD  =0x08
	def __init__(self):
		UsbMessage.__init__(self)

	def marshall(self):
		return struct.pack('<BH',self.cmd,0)

class UsbMsg2_GetPhoneState(UsbMessage):
	CMD  =0x08
	def __init__(self):
		UsbMessage.__init__(self)
		self.value=0

	def unmarshall(self,d):
		self.value, = struct.unpack('<I',d[:4])
		return True


class UsbMsg1_Dial(UsbMessage):
	CMD  =0x09
	def __init__(self):
		UsbMessage.__init__(self)
		self.number = ''

	def marshall(self):
		#错误啊，size 应该是后续字段大小，虽然是固定20但这里是要求实际电话号码长度
		number =''
		for c in self.number:
			number+=chr(int(c))
		number = number +'\x0f'*(20 - len(self.number) )
		return struct.pack('<BH20s',self.cmd,len(self.number),number)




class UsbMsg2_Ring(UsbMessage):
	CMD  =0x0b
	def __init__(self):
		UsbMessage.__init__(self)
		self.number = ''

	def unmarshall(self,d):

		self.number = normarlize_phonenum(d)
		return True


class UsbMsg2_NewSerial(UsbMessage):
	CMD  =0x0c
	def __init__(self):
		UsbMessage.__init__(self)
		self.serial = 0
		self.attr = 0   #0：来电；1：去电 2：录音
		self.number = ''

	def unmarshall(self,d):
		self.serial,self.attr = struct.unpack('<IB',d[:5])
		s = d[5:]
		self.number = normarlize_phonenum(s)

		return True

class UsbMsg2_Hangup(UsbMessage):
	CMD  =0x0d
	def __init__(self):
		UsbMessage.__init__(self)
		self.serial = 0
		self.attr = 0   #0：来电；1：去电 2：录音
		self.number = ''

	def unmarshall(self,d):
		self.serial,self.attr = struct.unpack('<IB',d[:5])
		s = d[5:]
		self.number = normarlize_phonenum(s)
		return True


class UsbMsg2_Dial(UsbMessage):
	CMD  =0x0a
	def __init__(self):
		UsbMessage.__init__(self)
		self.number = ''

	def unmarshall(self,d):
		self.number = normarlize_phonenum(d)
		return True

#振铃结束通知上位机
class UsbMsg2_RingEnd(UsbMessage):
	CMD  =0x12
	def __init__(self):
		UsbMessage.__init__(self)
		self.number = ''

	def unmarshall(self,d):
		self.number = normarlize_phonenum(d)
		return True


# class UsbMsg2_Dial(UsbMessage):
# 	CMD  =0x0a
# 	def __init__(self):
# 		UsbMessage.__init__(self)
# 		self.number = ''
#
# 	def unmarshall(self,d):
# 		s = d
# 		idx = s.find('\x0f')
# 		if idx!=-1:
# 			self.number = d[:idx]
# 		else:
# 			self.number = s
# 		return True


class UsbMsg1_Hangon(UsbMessage):
	CMD  =0x0f
	def __init__(self):
		UsbMessage.__init__(self)
		self.number = ''

	def marshall(self):
		return struct.pack('<BH',self.cmd,0)

class UsbMsg1_Hangup(UsbMessage):
	CMD  =0x0e
	def __init__(self):
		UsbMessage.__init__(self)
		self.number = ''

	def marshall(self):
		return struct.pack('<BH20s',self.cmd,0,'\x0f'*20)

#2013.10.9 add recording start and stop
class UsbMsg1_RecordStart(UsbMessage):
	CMD  =0x10
	def __init__(self):
		UsbMessage.__init__(self)

	def marshall(self):
		return struct.pack('<BH',self.cmd,0)

#2013.10.9 add recording start and stop
class UsbMsg1_RecordStop(UsbMessage):
	CMD  =0x11
	def __init__(self):
		UsbMessage.__init__(self)

	def marshall(self):
		return struct.pack('<BH',self.cmd,0)

EventMsgList=\
	(   UsbMsg2_Dial,
		UsbMsg2_GetFileContent,
	    UsbMsg2_GetFileInfo,
	    UsbMsg2_GetFileNumber,
	    UsbMsg2_GetPassowrd,
	    UsbMsg2_GetSerialNumber,
	    UsbMsg2_GetUserCode,
	    UsbMsg2_Hangup,
	    UsbMsg2_NewSerial,
	    UsbMsg2_Ring,
	    UsbMsg2_GetPhoneState,
	    UsbMsg2_PhoneDial,
	    UsbMsg2_RingEnd,    #振铃结束通知
	)


class UsbHost:
	_hanlde = None
	def __init__(self):
		self.passwd = None
		self.usercode = None
		self.current =None
		self.exitflag = True
		self.buff =''
		self.media_dir=''
		self.currserial = 0
		self.mainwin = None
		self.curr_dev_index = 0 #当前在线设备编号

		self.passwd = None
		self.usercode= None

		self.loadProperties()

	def saveProperties(self):
		from base import getApp
		try:
			usbfile = getApp().getBinPath()+'/usb.props'
			f = open(usbfile,'w')
			content = '%s'%(self.currserial)
			f.write(content)
			f.close()
		except:
			pass

	def loadProperties(self):
		from base import getApp
		try:
			usbfile = getApp().getBinPath()+'/usb.props'
			f = open(usbfile,'r')
			content = f.readline().strip()
			f.close()
			serial, = content.split(',')
			self.currserial = int(serial)
		except:
			pass


	def getUserCode(self,timeout=2):
		self.usercode = None
		m = UsbMsg1_GetUserCode()
		self.writeData(m.marshall())
		start = time.time()
		while not self.passwd:
			time.sleep(0.5)
			if time.time() > timeout:
				break
		return self.usercode

	def getPassword(self,timeout=2):
		self.passwd = None
		m = UsbMsg2_GetPassowrd()

		self.writeData(m.marshall())
		start = time.time()
		while not self.passwd:
			time.sleep(0.5)
			if time.time() > timeout:
				break
		return self.passwd


	def setUserCode(self,code):
		'''
			code - interge  ( 0 - 2^31 )
		'''
		m = UsbMsg1_SetUserCode()
		m.value = int(code)
		self.writeData(m.marshall())

	def getDeviceSerial(self):
		'''
			获取当前连接到的话机  硬件 编号
		'''
		buf = create_string_buffer(512)
		# size = pointer(c_uint(0))
		r = SI_GetProductString(self.curr_dev_index,buf,0)
		return buf


	def mediaDir(self,path=None):
		if not path:
			return self.media_dir
		self.media_dir = path

	def currentSerial(self,curr=None):
		if curr == None:
			return self.currserial
		self.currserial = curr
		self.saveProperties()

	def open(self):
		thread = threading.Thread(target=self._work_thread)
		thread.start()

	def close(self):
		self.exitflag = True
		print 'close...'
		if self.current:
			SI_Close(self.current)
			self.current = None

	def _work_thread(self):

		print 'usbhost start..'
		self.exitflag = False
		SI_SetTimeouts(2000,2000)
		last_sync_time = 0
		while not self.exitflag:
			#检测usb设备是否接驳
			self._searchDevice()
			if not self.current:
#				print 'no device detected'
				time.sleep(1)
				continue

			#读取话机主动上传的消息
			e,d = self.readDataBlocked()
			if e < 0:
				print 'read device exception occur!'
				continue
			if d:   #处理设备发送上来的消息
				msglist = self.parseMessage(d)
				for m in msglist:
					print m
					self.dispatch(m)
			print 'time tick test..'
			if time.time() - last_sync_time > 5 :
				try:
					self._syncFiles()
				except:
					traceback.print_exc()
				last_sync_time = time.time()
		print 'usbhost exited'


	def _syncFiles(self):
		from base import getApp

		m = UsbMsg1_GetPassword()
		m = self.sendMessage(m,UsbMsg2_GetPassowrd)
		if not m:
			print 'get passwd failed!'
			if self.mainwin:
				self.mainwin.signal_phonepasswd_status.emit(False,'')
			return False
		print 'phone passwd:',m.value
#		if m.value!='0000':
		if m.value!=getApp().getSettingsValue('phone_passwd'):
			print 'app phone passwd',getApp().getSettingsValue('phone_passwd')
			if self.mainwin:
				self.mainwin.signal_phonepasswd_status.emit(False,'')
			return False

		if self.mainwin:
			self.mainwin.signal_phonepasswd_status.emit(True,m.value)

#		return
#		print 'syncFiles...'
		if not os.path.exists(self.mediaDir()):
			os.mkdir(self.mediaDir())

		m = UsbMsg1_GetFileNumber()
		m = self.sendMessage(m,UsbMsg2_GetFileNumber)
		print m
		if not m:
			return False
		filenum = m.value
		if not filenum:
			return
		print 'audio num:',filenum
		m = UsbMsg1_GetSerialNumber()
		m = self.sendMessage(m,UsbMsg2_GetSerialNumber)
		if not m:
			return False
		print m,m.value
		newserial = m.value

		num = newserial - self.currentSerial()
		if num <= 0 :
			return True # no files need by syncing
		
		start = filenum - num

		print "filenum:%s,remain:%s,start:%s"%(filenum,num,start)
		if start < 0 :
			start = 0
		max_serial = 0
		for index in range(start,filenum):
			print 'start index:%s'%index
			m = UsbMsg1_GetFileInfo()
			m.value = index
			m = self.sendMessage(m,UsbMsg2_GetFileInfo)
			if not m:
				return False
			
			print '-- begin --'
			spx = format.parseSpxFileInfoByStream(m.value)
			print '-- end --'
			if not spx: continue
			if spx.filelen == 0xffff00:
				continue

			hdrinfo = m.value
			MAX_READ_SIZE = 512

			address = spx.fileaddr
			filelen = spx.filelen


#			ymd = '%04d-%02d-%02d'%(spx.year,spx.month,spx.day)
			ym = '%04d-%02d'%(spx.year,spx.month)

			path = os.path.join(self.mediaDir(),ym)
			if not os.path.exists(path):
				os.mkdir(path)
			path = os.path.join(self.mediaDir(),ym)
			if not os.path.exists(path):
				os.mkdir(path)

			spxfile = os.path.join(path,spx.filename()+'._spx_')
			finalname = os.path.join(path,spx.filename()+'.spx')
			print finalname
			if os.path.exists(finalname):
				print 'file is existed!'
				self.currentSerial(spx.serial)
				continue

			f = open(spxfile,'wb')
			f.write( hdrinfo )

			print 'incoming spx file-size:%s'%(hex(filelen))

			while filelen>0:
				m = UsbMsg1_GetFileContent()
				m.address = address
				if filelen >= MAX_READ_SIZE:
					m.blocksize = MAX_READ_SIZE
				else:
					m.blocksize = filelen
				filelen-=m.blocksize
				address+=m.blocksize
				# print hex(m.address),hex(m.blocksize)
				#print 'send msg:UsbMsg2_GetFileContent,blocksize:%s,m.address:%s'%(m.blocksize,hex(m.address))
				m = self.sendMessage(m,UsbMsg2_GetFileContent)
				#print 'return:%s',repr(m)
				if not m:
					print 'get file content is null'
					return False
				# print 'recieve data size:',len(m.value)
				# print filelen
				# time.sleep(400)
				f.write(m.value)
			f.close()
			#print 'rename file:',spxfile,finalname
			os.rename(spxfile,finalname)

			print 'usb-sync file:%s,%s ok'%(finalname,spx.serial), hex(spx.filelen),spx.duration
			self.currentSerial(spx.serial)
			#sys.exit()


	def reset(self):
		if self.current:
			SI_Close(self.current)
			self.current = None
		self.buff = ''
		if self.mainwin:
			self.mainwin.signal_device_disconnected.emit()

	def readDataBlocked(self):
		'''
			> 0     data return
			= 0     no data or timeout
			< 0     other error ,should close handle
		'''
		if not self.current:
			self.reset()
			return -1,''

		buf = create_string_buffer(1024*60)
		size = pointer(c_uint(0))
		# print 'xx',len(buf)
		# print 'blocked read..'
		r = SI_Read(self.current,buf,len(buf),size,0)
#		print r,size.contents.value

		psize = pointer(c_int(0))
		SI_GetNumDevices(psize)
#		print 'get num devices:',size.contents.value
		if psize.contents.value == 0:
#			print 'device lost!'
			self.reset()
			return -1,''

		if r==SI_READ_TIMED_OUT:

			return 0,''

		if r!=SI_SUCCESS:
			self.reset()
			return -1,''

		if size.contents.value:
			return size.contents.value,buf[:size.contents.value]
		return 0,''

	def parseMessage(self,d):
		result=[]
#		print 'buff remain:',len(self.buff)
		self.buff+=d
		while True:
			if len(self.buff) < 3:
				# print 'too small.. less hdrsize'
				break
			# cmd, = struct.unpack('B',self.buff[0])
			# size, = struct.unpack('H',self.buff[1:3])
			cmd,size = struct.unpack('<BH',self.buff[:3])
#			print 'cmd ,size:',cmd,size
			if len(self.buff) < size+3:
				# print 'too small..2'
				break
			content = self.buff[3:size+3]
			self.buff = self.buff[size+3:]
#			print 'buff size:',len(self.buff)
			m = None
			# print 'message content(%s):'%len(content),repr(content)
			for ecls in EventMsgList:
				if cmd == ecls.CMD:
					# print 'command:',cmd
					m = ecls()  #实例化消息类
					if not m.unmarshall(content):
						m = None
						break
			if m:
				result.append(m)
		return result



	def readData(self):
		'''
			> 0     data return
			= 0     no data or timeout
			< 0     other error ,should close handle
		'''
		size = self.getRxQueueDataSize()
		if size > 0 :
			buf = create_string_buffer(1024*60)
			size = pointer(c_uint(0))
			r = SI_Read(self.current,buf,len(buf),size,0)

			if r!=SI_SUCCESS:
				self.reset()
				return ''
			if size.contents.value:
				return buf[:size.contents.value]

		return ''



	def _searchDevice(self):
		if not self.current:
			size = pointer(c_int(0))
			r = SI_GetNumDevices(size)
			if r !=  SI_SUCCESS:
				return
			if size.contents.value == 0 :
				return
			idx = 0
			handle = pointer(c_uint(0))
			r = SI_Open(idx,handle)
			if r != SI_SUCCESS:
				print 'try si_open(%s) failed!'%(idx)
				return
			if handle.contents.value == 0:
				print 'device handle is NULL,si_open failed!'
				return
			self.current = handle.contents.value
			print 'handle:%s be openned!'%str(self.current)
			if self.mainwin:
				self.mainwin.signal_device_connected.emit()
			SI_FlushBuffers(self.current,0,0)



	def phoneDial(self,number):
		if not self.current:
			return
		m = UsbMsg1_Dial()
		m.number= number
		self.writeData(m.marshall())


	def writeData(self,d):
		if not self.current:
			return False
#		print 'byte writen:',repr(d)
		d = create_string_buffer(d)
		written = pointer(c_uint(0))
		r = SI_Write(self.current,d,len(d),written,0)
		return written

	def phoneHangup(self):
		m = UsbMsg1_Hangup()
		self.writeData(m.marshall())

	def phoneHangon(self):
		m = UsbMsg1_Hangon()
		self.writeData(m.marshall())

	def recordStart(self):
		m = UsbMsg1_RecordStart()
		self.writeData(m.marshall())

	def recordStop(self):
		m = UsbMsg1_RecordStop()
		self.writeData(m.marshall())

	def onPhoneRinging(self,number):
		if not self.mainwin: return
		self.mainwin.signal_phoneRing.emit(number)

	def onPhoneRingEnd(self,number):
		if not self.mainwin: return
		self.mainwin.signal_phonering_end.emit()

	def onPhoneNewSerial(self,serial,attr,number):
		if not self.mainwin: return
		print 'UsbMsg: NewSerial=%s,%s,%s'%(serial,attr,number)
		self.mainwin.signal_phoneNewSerial.emit(number,attr,serial)


	def onPhoneHangon(self):
		pass

	def onPhoneHangup(self):
		if not self.mainwin: return
		self.mainwin.signal_phoneHangup.emit()

	def onPhoneDail(self,number):
		'''
			话机主动拨打电话，发送通知到上位机
		'''
		if not self.mainwin: return
		self.mainwin.signal_phoneDial.emit(number)

	def getDevicePasswd(self):
		passwd = ''
		if not self.current:
			return ''
		SI_SetTimeouts(3000,3000)
		d = struct.pack('!BH',4,0)
		s = create_string_buffer(d)
		size = pointer(c_uint(0))
		r = SI_Write(self.current,s,len(d),size,0)
		size = self.getRxQueueDataSize()


	def getRxQueueDataSize(self):
		handle = self.current
		if not handle:
			return 0
		size = pointer(c_uint(0))
		status = pointer(c_uint(0))
		r = SI_CheckRXQueue(handle,size,status)
		# print 'pp',r,size.contents.value
		if r != SI_SUCCESS:
			self.reset()
			return 0
		return size.contents.value

	def sendMessage(self,m,expectCLS):
		'''
			m - 发送到设备的消息
		'''
		self.writeData(m.marshall())
		e,d = self.readDataBlocked()
		# print 'read data:',e,d
		r = None
		if d :
			msglist = self.parseMessage(d)
			for m in msglist:
			# m = msglist[0]
				if not isinstance(m,expectCLS):#如果不是期待的返回消息，则分派处理那些主动触发的消息
					self.dispatch(m)
				else:
					r = m 
		return r

	def postMessage(self,m):
		'''
			m - 发送到设备的消息
		'''
		self.writeData(m.marshall())

	def dispatch(self,m):
		'''
			@return : boolean
		'''

		if isinstance(m,UsbMsg2_Ring):
			self.onPhoneRinging(m.number)
		if isinstance(m,UsbMsg2_NewSerial):
			self.onPhoneNewSerial(m.serial,m.attr,m.number)
		if isinstance(m,UsbMsg2_Hangup):
			self.onPhoneHangup()
		if isinstance(m,UsbMsg2_PhoneDial):
			self.onPhoneDail(m.number)
		if isinstance(m,UsbMsg2_GetPassowrd):
			self.passwd = m.value
		if isinstance(m,UsbMsg2_GetUserCode):
			self.usercode = m.value
		if isinstance(m,UsbMsg2_RingEnd):
			self.onPhoneRingEnd(m.number)


	@classmethod
	def instance(cls):
		if not cls._hanlde:
			cls._hanlde = cls()
		return cls._hanlde
def test():
	start = time.time()
	UsbHost.instance()._searchDevice()
	SI_SetTimeouts(10000,10000)
	SI_FlushBuffers(UsbHost.instance().current,0,0)
	# UsbHost.instance().phoneDial('8015')
	# time.sleep(5)
	# d = UsbMsg1_SetUserCode()
	# d.value=0x11223344
	# UsbHost.instance().writeData(d.marshall())
	# time.sleep(1)
	# d = UsbMsg1_GetUserCode()
	# UsbHost.instance().writeData(d.marshall())

	while True:
		e,d = UsbHost.instance().readDataBlocked()
		print e,d
		if not d:
			if time.time() - start >10:
				print 'exec hang up..'
				# UsbHost.instance().phoneHangup()
				start = 0xffffffff

			print 'time out'
			continue
		print repr(d)
		msglist = UsbHost.instance().parseMessage(d)
		print msglist
		for m in msglist:
			if isinstance(m,UsbMsg2_Ring):
				print 'ring:',m.number,repr(m.number)
			if isinstance(m,UsbMsg2_NewSerial):
				print 'new serial:',m.serial,m.attr,m.number,repr(m.number)
			if isinstance(m,UsbMsg2_Hangup):
				print 'hang up:',m.serial,m.attr,m.number,repr(m.number)
			if isinstance(m,UsbMsg2_GetUserCode):
				print 'get usercode:',m.value,hex(m.value),repr(m.value)
	return

	m = UsbMsg1_GetFileNumber()
	m = UsbHost.instance().sendMessage(m,UsbMsg2_GetFileNumber)
	UsbHost.instance().mediaDir(r'C:\leadtel\media')
	UsbHost.instance()._syncFiles()

	return






def test2():
	# size = pointer(c_int(0))
	# r = SI_GetNumDevices(size)
	# print r,size.contents.value
	UsbHost.instance()._searchDevice()

	SI_SetTimeouts(400000,4000000)

	read = pointer(c_uint(0))
	write = pointer(c_uint(0))
	# SI_GetTimeouts(read,write)
	# print read.contents.value,write.contents.value

	SI_FlushBuffers(UsbHost.instance().current,0,0)

	# while 1:
	# 	print UsbHost.instance().getRxQueueDataSize()
	# 	time.sleep(1)

	# UsbHost.instance().getDevicePasswd()
	# time.sleep(1)
	#print UsbHost.instance().getRxQueueDataSize()
	# d = UsbHost.instance().readDataBlocked()


	# UsbHost.instance().phoneDial('10000')
	# time.sleep(5)
	# UsbHost.instance().phoneHangup()
	# time.sleep(5)

	# d = UsbMsg1_GetPhoneState()
	# UsbHost.instance().writeData(d.marshall())
	# time.sleep(1)

	# d = UsbMsg1_SetUserCode()
	# d.value=0x11223322
	# UsbHost.instance().writeData(d.marshall())

	# d = UsbMsg1_SetUserCode()
	# d.value=0x11223355
	# UsbHost.instance().writeData(d.marshall())
	#
	# d = UsbMsg1_GetUserCode()
	# UsbHost.instance().writeData(d.marshall())
	#
	# d = UsbMsg1_GetSerialNumber()
	# UsbHost.instance().writeData(d.marshall())
	#
	d = UsbMsg1_GetFileNumber()
	UsbHost.instance().writeData(d.marshall())

	# d =UsbMsg1_GetFileInfo()
	d.value = 130
	# UsbHost.instance().writeData(d.marshall())

	# return
	print 'ready for read..'

	filenum = 0
	curserial = 0
	filelist=[]
	while True:
		if filelist:
			d =UsbMsg1_GetFileInfo()
			d.value = filelist[0]
			UsbHost.instance().writeData(d.marshall())

		e,d = UsbHost.instance().readDataBlocked()
		print 'read data:',e,d
		if d :
			msglist = UsbHost.instance().parseMessage(d)
			print msglist
			for m in msglist:
				if isinstance(m,UsbMsg2_GetPassowrd):
					print 'UsbMsg2_GetPassowrd:',m.value
				if isinstance(m,UsbMsg2_GetPhoneState):
					print 'UsbMsg2_GetPhoneState:',repr(m.value),hex(m.value)
				if isinstance(m,UsbMsg2_GetUserCode):
					print 'UsbMsg2_GetUserCode:',repr(m.value),hex(m.value)
				if isinstance(m,UsbMsg2_GetSerialNumber):
					print 'UsbMsg2_GetSerialNumber:',repr(m.value),hex(m.value)
					if filenum:
						if m.value - curserial > filenum:
							curserial = m.value - filenum
							filelist = range(curserial,m.value)


				if isinstance(m,UsbMsg2_GetFileNumber):
					print 'UsbMsg2_GetFileNumber:',repr(m.value),hex(m.value)
					d = UsbMsg1_GetSerialNumber()
					UsbHost.instance().writeData(d.marshall())
					filenum = m.value

				if isinstance(m,UsbMsg2_GetFileInfo):
					print 'UsbMsg2_GetFileInfo:',repr(m.value)
					spx = format.parseSpxFileInfoByStream(m.value)
					if filelist:
						del filelist[0]





if __name__=='__main__':
	test()
	sys.exit()


