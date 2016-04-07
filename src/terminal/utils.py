# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib,threading
import datetime

def getmtime(file):
	try:
		return os.path.getmtime(file)
	except: return 0
	
def getfiledigest(file,bufsize=1024*5,type='md5'):
	import hashlib
	m = hashlib.md5()
	try:
		fp = open(file,'rb')
		while True:
			data = fp.read(bufsize)
			if not data:break
			m.update(data)
		fp.close()
		return m.hexdigest()
	except:
		traceback.print_exc()
		return ''

def getdigest(d,bufsize=1024*5,type='md5'):
	import hashlib
	try:
		m = hashlib.md5()
		m.update(d)
		return m.hexdigest()
	except:
		return ''
	
def setmtime(file,tick): # tick - unix timestamp 1970~
	os.utime(file,(tick,tick) )
	
def getdbsequence_pg(dbconn,seqname):
	seq = 0
	try:
		sql = "select nextval('%s')"%seqname
		cr = dbconn.cursor()
		cr.execute(sql)
		seq = cr.fetchone()[0]
	except:
		traceback.print_exc()
	return seq


def loadjson(file):
	d = None
	try:
		fd = open(file)
		cont = fd.read().strip()
		cont = cont.replace(' ','')
		cont = cont.replace('\'',"\"")
		cont = cont.replace('\t',"")
		cont = cont.replace('(',"[")
		cont = cont.replace(')',"]")
#		print cont
		fd.close()
		d = json.loads(cont)
	except:
		traceback.print_exc()
		pass #traceback.print_exc()
	return d
	
def waitForShutdown():
	time.sleep(1*10000*10)

def genTempFileName():
	return str(time.time())

# unix timestamp to datetime.datetime	
def mk_datetime(timestamp):
	timestamp = int(timestamp)
	return datetime.datetime.fromtimestamp(timestamp)

def formatTimestamp(secs):
	try:
		dt = datetime.datetime.fromtimestamp(secs)
		return "%04d-%02d-%02d %02d:%02d:%02d"%(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
	except:
		return ''

def formatTimestamp2(secs):
	try:
		dt = datetime.datetime.fromtimestamp(secs)
		return "%04d.%02d.%02d %02d:%02d:%02d"%(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
	except:
		traceback.print_exc()
		return ''

def formatTimestamp_ymdhm(secs):
	try:
		dt = datetime.datetime.fromtimestamp(secs)
		return "%04d-%02d-%02d %02d:%02d"%(dt.year,dt.month,dt.day,dt.hour,dt.minute)
	except:
		return ''

def formatTimeLength(secs):
	h = int(secs/3600)
	secs = secs%3600
	m = int(secs/60)
	s = secs%60
	return '%02d:%02d:%02d'%(h,m,s)
#根据datetime产生timestamp	
def maketimestamp(dt):
	if not dt:
		return 0
	return time.mktime(dt.timetuple())

def touchfile(file):
	try:
		fp = open(file,'w')
		fp.close()
	except:
		return False
	return True

def getToDayStr():
	t = time.localtime()
	return "%04d%02d%02d"%(t.tm_year,t.tm_mon,t.tm_mday)

def getToDayStr2():
	t = time.localtime()
	return "%04d-%02d-%02d"%(t.tm_year,t.tm_mon,t.tm_mday)
	
#这个class用于异步等待获取返回对象之用
class MutexObject:
	def __init__(self):
		self.mtx = threading.Condition()
		self.d = None
		
	def waitObject(self,timeout):
		d = None
		self.mtx.acquire()
		if self.d == None:
			self.mtx.wait(timeout)
			d = self.d
			self.d = None
		self.mtx.release()
		return d
		
	def notify(self,d):
		self.mtx.acquire()
		self.d = d
		self.mtx.notify()
		self.mtx.release()

def geo_rect2wktpolygon(rc):
	# rc - (x,y,w,h)
	x,y,w,h = rc
	return "POLYGON((%s %s,%s %s,%s %s,%s %s,%s %s))"%\
		(x,y,x+w,y,x+w,y+h,x,y+h,x,y)

def readImageTimes(imagefile,ffmpeg='ffmpeg.exe'):
	import re
	
	rst = () # (creattime,lastmodifytime) timestamp time ticks
	detail = os.popen3('%s -i %s'%(ffmpeg,imagefile) )[2].read()
	tt = re.findall('Duration: (\d{1,2}:\d{1,2}:\d{1,2}\.\d{0,4}),',detail,re.M)
	if tt:
		tt = tt[0]
	else:
		return (0,0)
	h,m,s = map(int, map(float,tt.split(':')) )
	duration_secs =  int ( h*3600 + m * 60 + s)
	lastmodify = os.path.getmtime(imagefile)
	createsecs =  lastmodify - duration_secs
	return (int(createsecs),int(lastmodify))

def statevfs(path):
	import win32api
	import os.path
	path = os.path.normpath(path)
	if path[-1]=='\\':
		path = path[:-1]
	try:
		f,all,user = win32api.GetDiskFreeSpaceEx(path)
		return all,user
	except:return 0,0
	
def hashobject(obj):
	attrs = [s for  s in dir(obj) if not s.startswith('__')]
	kvs={}
	for k in attrs:
		kvs[k] = getattr(obj, k)
	#kvs = {k:getattr(obj, k) for k in attrs}
	return kvs

MB_SIZE = 1024.*1024.
def formatfilesize(size):
	mb = round(size/MB_SIZE,3)
	return mb



def readImageTimes(imagefile,ffmpeg='ffmpeg.exe'):
	import re
	rst = () # (creattime,lastmodifytime) timestamp time ticks
	imagefile = os.path.normpath(imagefile)
	detail = os.popen3('ffmpeg.exe -i %s'%(imagefile) )[2].read()
	tt = re.findall('Duration: (\d{1,2}:\d{1,2}:\d{1,2}\.\d{0,4}),',detail,re.M)
	if tt:
		tt = tt[0]
	else:
		return ()
	h,m,s = map(int, map(float,tt.split(':')) )
	duration_secs =  int ( h*3600 + m * 60 + s)
	lastmodify = os.path.getmtime(imagefile)
	createsecs =  lastmodify - duration_secs
	return (int(createsecs),int(lastmodify))

def readImageDuration(imagefile,ffmpeg='ffmpeg.exe'):
	import re
	rst = () # (creattime,lastmodifytime) timestamp time ticks
	print 'readImageDuration'
	print imagefile
	imagefile = os.path.normpath(imagefile)
	cmd = u'ffmpeg.exe -i "%s"'%(imagefile)
	detail = os.popen3(cmd.encode('gbk') )[2].read()
	print 'cmd:',cmd
	print 'pipe result:',detail
	tt = re.findall('Duration: (\d{1,2}:\d{1,2}:\d{1,2}\.\d{0,4}),',detail,re.M)
	if tt:
		tt = tt[0]
	else:
		return 0
	h,m,s = map(int, map(float,tt.split(':')) )
	duration_secs =  int ( h*3600 + m * 60 + s)
	return duration_secs


def parseInetAddress(address):
	try:
		host,port=address.split(':')
		port = int(port)
		return host,port
	except:
		return ()

class SimpleConfig:
	def __init__(self):
		self.confile =''
		self.props={}

	def load(self,file):
		try:
			f = open(file,'r')
			lines = f.readlines()
			f.close()
			self.props={}
			for line in lines:
				line = line.strip()
				if not line or line[0]=='#':
					continue
				line = line.split('#')[0]
				pp = line.split('=')
				if len(pp)!=2:
					continue
				k,v = pp[0].strip(),pp[1].strip()
				self.props[k] = v
		except:
			traceback.print_exc()
			self.props ={}
		return self

	def get(self,key,default=None):
		return self.props.get(key,default)

def multi_get_letter(str_input):  
      
    if isinstance(str_input, unicode):  
        unicode_str = str_input  
    else:  
        try:  
            unicode_str = str_input.decode('utf8')  
        except:  
            try:  
                unicode_str = str_input.decode('gbk')  
            except:  
                print 'unknown coding'  
                return  
      
    return_list = []  
    for one_unicode in unicode_str:  
        #print single_get_first(one_unicode)  
        return_list.append(single_get_first(one_unicode))  
    return "".join(return_list)      
      
def single_get_first(unicode1):  
    str1 = unicode1.encode('gbk')  
    try:          
        ord(str1)  
        return str1  
    except:  
        asc = ord(str1[0]) * 256 + ord(str1[1]) - 65536  
        if asc >= -20319 and asc <= -20284:  
            return 'a'  
        if asc >= -20283 and asc <= -19776:  
            return 'b'  
        if asc >= -19775 and asc <= -19219:  
            return 'c'  
        if asc >= -19218 and asc <= -18711:  
            return 'd'  
        if asc >= -18710 and asc <= -18527:  
            return 'e'  
        if asc >= -18526 and asc <= -18240:  
            return 'f'  
        if asc >= -18239 and asc <= -17923:  
            return 'g'  
        if asc >= -17922 and asc <= -17418:  
            return 'h'  
        if asc >= -17417 and asc <= -16475:  
            return 'j'  
        if asc >= -16474 and asc <= -16213:  
            return 'k'  
        if asc >= -16212 and asc <= -15641:  
            return 'l'  
        if asc >= -15640 and asc <= -15166:  
            return 'm'  
        if asc >= -15165 and asc <= -14923:  
            return 'n'  
        if asc >= -14922 and asc <= -14915:  
            return 'o'  
        if asc >= -14914 and asc <= -14631:  
            return 'p'  
        if asc >= -14630 and asc <= -14150:  
            return 'q'  
        if asc >= -14149 and asc <= -14091:  
            return 'r'  
        if asc >= -14090 and asc <= -13119:  
            return 's'  
        if asc >= -13118 and asc <= -12839:  
            return 't'  
        if asc >= -12838 and asc <= -12557:  
            return 'w'  
        if asc >= -12556 and asc <= -11848:  
            return 'x'  
        if asc >= -11847 and asc <= -11056:  
            return 'y'  
        if asc >= -11055 and asc <= -10247:  
            return 'z'  
        return ''  
		

class Logger:
	def __init__(self):
		self.handlers=[]
		self.dumpEnabled = False    #默认不启动日志输出
		if os.path.exists('logdump.yes'):
			self.dumpEnabled = True

	__handle = None
	@staticmethod
	def instance():
		if not Logger.__handle:
			Logger.__handle = Logger()

		return Logger.__handle

	def addHandler(self,h):
		self.handlers.append(h)

	def info(self,s):
		self.write(s,'INFO')
	
	def error(self,s):
		self.write(s,'ERROR')
		
	def debug(self,s):
		self.write(s)
		
	def write(self,s,level='DEBUG'):
		if not self.dumpEnabled:
			return

		import time
		if not s.strip():
			return 
		stime = formatTimestamp(int(time.time()))
		s = stime + ' %s '%level + s 
		for h in self.handlers:
			try:
				h.write(s)
			except:
				traceback.print_exc()

	def writelines(self,text,level='DEBUG'):
		#text = text.strip()
		self.write(text+'\n',level)


	class StdoutHandler:
		def __init__(self,stdout=None):
			self.stdout = stdout

		def write(self,s):
			if self.stdout:
				try:
					self.stdout.write(s+'\n')
				except:					
					self.stdout.write(s.encode('gbk')+'\n')


	class FileHandler:
		def __init__(self,file,mode='a+'):
			self.file = file
			self.mode = mode
			self.hfile = None

		def write(self,s):
			if not self.hfile:
				self.hfile = open(self.file,self.mode)
			if self.hfile:
				try:
					self.hfile.write(s+'\n')
				except:
					self.hfile.write(s.encode('gbk')+'\n')
				self.hfile.flush()

	class DatagramHandler:
		def __init__(self,dest=('127.0.0.1',17948)):
			self.dest = dest
			self.sock = None

		def write(self,s):
			import socket
			if not self.sock:
				self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			try:
				self.sock.sendto(s,0,self.dest)
			except:
				self.sock.sendto(s.encode('gbk'),0,self.dest)


def setAutoRunWithOsStart(key,app,start=True):
	import _winreg
	try:
		r = _winreg.OpenKey(
		         _winreg.HKEY_LOCAL_MACHINE,
		        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",0,_winreg.KEY_WRITE)
		if start:
			_winreg.SetValueEx(r,key,0,_winreg.REG_SZ,app)
		else:
			_winreg.DeleteValue(r,key)
	except:
		traceback.print_exc()

def getRegisterValueInAutoRun(key='audioTerm'):
	import _winreg
	try:
		r = _winreg.OpenKey(
		         _winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")

		p1,num,p3 = _winreg.QueryInfoKey(r)
		for n in range(num):
			p1,p2,p3 =  _winreg.EnumValue(r,n)
			if p1 == key:
				return p2
	except:
		traceback.print_exc()
		return None

def killProcess(pid):
	import subprocess
	# handle = subprocess.Popen("", shell=False)
	subprocess.Popen("taskkill /F /T /PID %i"%pid , shell=True)


class Win32:
	@staticmethod
	def dispatchMessage(winid):
		import win32api,win32gui,win32con
		status, msg = win32gui.PeekMessage(winid,0,0,win32con.PM_NOREMOVE)
		if not msg[0] == 0:
			b,msg = win32gui.GetMessage(winid,0,0)
			if msg:
				win32gui.TranslateMessage(msg)
				win32gui.DispatchMessage(msg)


def loadValuesFromFile(filename):
	values={}
	try:
		f = open(filename)
		content = f.readlines()
		f.close()
		for line in content:
			line = line.strip()
			if not line: continue
			values[line]=None
	except:
		values={}
	return values.keys()

def saveValuesToFile(filename,values):
	try:
		f = open(filename,'w')
		for val in values:
			f.write(val+'\n')
		f.close()
	except:
		return False
	return True

def normalizeString(s):
	if not s:
		return ''
	return s


def getScreenSize():
	#from win32api import GetSystemMetrics
	import win32api
	return win32api.GetSystemMetrics(0),win32api.GetSystemMetrics(1)

def checkPasswdStr(passwd):
	'''
		检查密码必须为 字母 + 数字
	'''
	import string
	letter = 0
	digit = 0
	for c in passwd:
		if c in string.ascii_letters:
			letter+=1
		if c in string.digits:
			digit+=1
	if digit!=0 and letter!=0:
		return True
	return False


def createProcessNoBlock(exe,params):
	import win32process
	command = exe +' '+params
	win32process.CreateProcess(None,command,None,None,0,0,None,None,win32process.STARTUPINFO())



if __name__=='__main__':
	#print loadjson('node.txt')
	#print statevfs('d:/temp4/')
	#print getfiledigest('D:/test_dvr_data/stosync/file0014.trp')
	#print readImageTimes(u'P:/20120523/沪EN3870/1-2/DCIM/100MEDIA/FILE0006.MOV'.encode('gbk'))
#	print SimpleConfig().load('system.conf').get('inv_cancel_mode')
	# u,all = statevfs('c:/temp')
	# print u/1024/1024/1024,all/1024/1024/1024
	#print sc.props

	#setAutoRunWithOsStart('audioTerm',r'c:\abc.exe',True)
	#r = getRegisterValueInAutoRun('audioTerm')
	#print repr(r)
	print getScreenSize()
