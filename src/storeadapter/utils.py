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
		return "%04d%02d%02d %02d:%02d:%02d"%(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
	except:
		return ''

def formatTimestamp2(secs):
	try:
		dt = datetime.datetime.fromtimestamp(secs)
		return "%04d.%02d.%02d %02d:%02d:%02d"%(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
	except:
		traceback.print_exc()
		return ''
	
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
	detail = os.popen3('c:/dvr_bin/ffmpeg.exe -i %s'%(imagefile) )[2].read()
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

if __name__=='__main__':
	#print loadjson('node.txt')
	#print statevfs('d:/temp4/')
	#print getfiledigest('D:/test_dvr_data/stosync/file0014.trp')
	#print readImageTimes(u'P:/20120523/沪EN3870/1-2/DCIM/100MEDIA/FILE0006.MOV'.encode('gbk'))
	print SimpleConfig().load('system.conf').get('inv_cancel_mode')

	#print sc.props


