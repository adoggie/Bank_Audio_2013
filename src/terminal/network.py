# -- coding:utf-8 --
# network.py 
# bin.zhang@sw2us.com 
# 2012.3.8
# revision:  
#

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,threading
import select

import message
from message import * 
from errbase import *

global_compress_type = COMPRESS_ZLIB
#global_compress_type = COMPRESS_NONE
		
#NetPacketQueue 处理消息分解
class NetPacketQueue:
	def __init__(self,conn = None,size= 1024):
		self.size = size
		self.outs={}
		self.ins={}
		self.user=None
		self.conn = conn
		self.bf=''
		self.pktlist=[] #解出来的消息
		self.mtxptks=threading.Condition()
		self.invalid = False 
	
	def clearPackets(self):
		self.mtxptks.acquire()
		self.pktlist=[]
		self.mtxptks.release()
		
	def destroy(self):
		self.invalid = True
		self.mtxptks.acquire()
		self.mtxptks.notify()
		self.mtxptks.release()


	def getMessage(self,timeout_sec=5):
		m = None		
		self.mtxptks.acquire()
		if self.pktlist:
			m = self.pktlist[0]
			del self.pktlist[0]
		else:
			#print 'wait:',timeout_sec,time.time()
			self.mtxptks.wait(timeout_sec)
			#print time.time()
			if self.pktlist:
				m = self.pktlist[0]
				del self.pktlist[0]
		self.mtxptks.release()
		#print 'getmessage:',m
		return m

	def getMessageList(self):
		m =[]		
		self.mtxptks.acquire()
		m = self.pktlist
		self.pktlist=[]
		self.mtxptks.release()
		return m
		
	'''
		@return: false - 脏数据产生 
	'''
	def dataQueueIn(self,d):
		
		
		rc = (True,2) # 2表示ok
		self.bf+=d
		d = self.bf
		while True:			
			hdrsize = NetMetaPacket.minSize()
			#print hdrsize,len(d)
			if len(d)<NetMetaPacket.minSize():				
				rc = True,0 #数据不够,等待
				break
			magic,size,compress,encrypt,ver = struct.unpack('!IIBBI',d[:hdrsize])
			if magic != NetMetaPacket.magic4:
				return False, NETMSG_ERROR_MAGIC#
			if size<=10:
				return False,NETMSG_ERROR_SIZE
			if len(d)< size+4:
				rc = True,1 #数据不够
				break
			size-=10
			#print size,compress,encrypt,ver
			s = d[hdrsize:hdrsize+size]
			d = d[hdrsize+size:]
			if compress == message.COMPRESS_ZLIB:
				try: 
					s = zlib.decompress(s)
				except:
					return False,NETMSG_ERROR_DECOMPRESS
			elif compress != message.COMPRESS_NONE:
				return False,NETMSG_ERROR_NOTSUPPORTCOMPRESS
			# restore to NetMetaPacket
			#MessageBase
			m = MessageBase.unmarshall(s)
			if m == None:
				return False,NETMSG_ERROR_MESSAGEUNMARSHALL
			self.mtxptks.acquire()
			self.pktlist.append(m)
			self.mtxptks.notify()			
			self.mtxptks.release()
		self.bf = d
		return rc
	
class NetConnThread:
	def __init__(self,conn,id='',proc=None):
		self.conn = conn
		if not proc:
			proc = self.inner
		self.thread = threading.Thread(target=proc)
		self.thread.start()
		self.id = id
	
	def join(self):
		self.thread.join()
		
	def inner(self):
#		print 'service threading entering...'
		import select
		while True:
			fds = [self.conn.sock]
			try:
				rds,wds,eds = select.select(fds,[],[],1)
				if not rds:
					continue
				d = self.conn.recvData()
				#print 'recv data:',d
				if not d:
					self.conn.close()
					break
	
				self.conn.eventDataRecv(d)		
			except:
				#traceback.print_exc()
				self.conn.close()
				break
		self.conn.eventDestroyed()
#		print 'NetConnThread Exiting...'

class NetConnectionEvent:
	EVENT_CONNECTED=1
	EVENT_DATA=2
	EVENT_DISCONNECTED=3
	def __init__(self,type,conn,data=None):
		self.type = type
		self.conn = conn
		self.data = data
		
class NetConnection:
	def __init__(self,sock=None,svc=None,recvfunc=None,queuecls=NetPacketQueue):
		self.service =svc
		self.sock = sock
		self.delta = None
		self.recvfunc = recvfunc		
		self.queue = queuecls(self)
		self.mtxmsg = threading.Condition()
	
	def getService(self):
		return self.service
		
	def getQueue(self):
		return self.queue
		
	def peer(self):
		pass
	
	def connect(self,dest):
		self.sock = socket.socket()
		try:			
			self.sock.connect(tuple(dest))
		except:
			#traceback.print_exc()
			return False
		return True
	'''	
	def setDataRecvFunc(self,funcRecv):
		recvfunc = funcRecv
	'''
	def eventDataRecv(self,data):
		r = False
		
		r,err = self.queue.dataQueueIn(data)
		if not r:
			self.close() #数据解码错误，直接关闭连接
			return
		msglist=[]
		#有一种情况app直接到connect.queue去获取,thread只是驱动读取数据并放入connection的queue队列
		if self.service or self.recvfunc:
			msglist = self.queue.getMessageList()
		if len(msglist) == 0:
			return
		self.mtxmsg.acquire()
		self.mtxmsg.notify()  #通知外部用户消息已经来了
		self.mtxmsg.release()
		#直接将数据抛给service接收处理 
		if self.service:
			try:
				self.service.eventGotMessage( msglist ,self ) #由到这里将消息直接弹射给用户，需要独立的或多个线程做支持
			except:
				traceback.print_exc()
		#如果是无service的connection对象接收数据需要构建一个thread对象，且在另外线程调用 conn.queue.getMessage()获取消息包
		if self.recvfunc:
			evt = NetConnectionEvent(NetConnectionEvent.EVENT_DATA,self,msglist)
			try:
				self.recvfunc(evt)
			except:traceback.print_exc()
		
	def recvData(self,size=1024):
		return self.sock.recv(size)
		
	def sendData(self,d):
		try:			
			self.sock.sendall(d)			
		except:
			traceback.print_exc()
			self.close()

			return False
		return True
	
	
	##等待是否有消息到达
	#def waitMessage(self,timeout=5):
	#	ms = []
	#	if 
	#	try:
	#		d = self.recvData()
	#		r = self.queue.dataQueueIn(d)
	#		if not r:
	#			self.close()
	#			return None
	#		self.queue.
	#	except:
	#		pass
		
	def sendMessage(self,m):
		try:
			d = NetMetaPacket(msg=m,compress=global_compress_type).marshall()
			#print 'sendmsg:',m.getMsg(),len(d),d
			self.sock.sendall(d)			
		except:
			traceback.print_exc()
			self.close()

			return False
		return True
			
	def close(self):	
		try:
			'''
				python bug:
				这里关闭套接字，但不能通知到此刻正在读取套接字的线程
				线程读取考虑采用select
			'''
			#self.sock.shutdown(socket.SHUT_RDWR)
			self.sock.close()		
		except:
			traceback.print_exc()
	
	def eventDestroyed(self):
		self.queue.destroy()	
		if self.service:
			self.service.eventConnDisconnected(self)
			
		if self.recvfunc:
			evt = NetConnectionEvent(NetConnectionEvent.EVENT_DISCONNECTED,self)
			self.recvfunc(evt)
		
class NetService:
	def __init__(self,name,addr,queuecls=NetPacketQueue):
		self.name = name
		self.addr = addr
		self.queuecls = queuecls
		
		self.condexit = threading.Condition()
		self.sock = None
		self.mtxconns = threading.Lock()
		self.conns=[]
		
		
	def eventConnCreated(self,conn):
		print 'conn created'
		self.mtxconns.acquire()
		self.conns.append(conn)
		self.mtxconns.release()
	
	def eventConnDisconnected(self,conn):
		print 'conn disconnected'
		self.mtxconns.acquire()
		self.conns.remove(conn)
		self.mtxconns.release()
	
	#service模式下接收的消息从这里冒上来
	# conn - 从哪个连接上接收的数据
	def eventGotMessage(self,msglist,conn):
		pass
	
	#将连接设置为select模式
	def selectConnIn(self,conn):
		pass
	
	def getConnections(self):
		pass
	
	def start(self):
		try:
			
			self.sock = socket.socket()
			#print 'lll',self.addr
			self.sock.bind( tuple(self.addr) )
			self.sock.listen(5)
			
			self.thread = threading.Thread(target=self.service_loop)
			self.thread.start()
			return True		
		except:
			traceback.print_exc()
			return False
		
	def shutdown(self):
		self.sock.close()
		self.mtxconns.acquire()
		for c in self.conns:
			c.close()
		self.mtxconns.release()
	
	def service_loop(self):
		print 'service:(%s) thread starting...'%self.name
		while True:
			fdr = []
			fdr.append(self.sock)
			infds,wr,e = select.select(fdr,[],[])
			if e:
				print 'service thread exit...'
				break
			for s in infds:
				if s == self.sock: #新连接到达 
					sock = None
					try:
						sock,peer = self.sock.accept()	#异常产生表示self.sock被强行关闭				
					except: 
						print 'service:(%s) thread exiting...'%self.name
						return 
					conn = NetConnection(sock,self,queuecls=self.queuecls) #动态数据队列对象
					#sock.delta['conn'] = conn					
					self.eventConnCreated(conn)					
		##
		
		#self.condexit.nofity()
		
		
class NetworkServer:
	def __init__(self,name=''):
		self.name = name
		self.services={}
		setattr(socket.socket,'delta',{})
		setattr(socket.socket,'conn',None)

	def createService(self,name,addr,port,servicecls=NetService):
		svc = serviccls(name,addr,port)
		self.services[name]=svc
		return svc
	
	def addService(self,serv):
		self.services[serv.name]=serv
	

		
		
def test_packetqueue():
	q = NetPacketQueue()
	for n in range(3*10):
		d = NetMetaPacket(msg=MsgCallReturn(value=[n],bin='A'*(n+1) ),compress=COMPRESS_ZLIB).marshall()
		q.dataQueueIn(d)
'''	
	while True:
		m = q.getMessage()
		if not m:
			break
		print m.attrs,m.bin
'''

class MyService(NetService):
	def __init__(self,name,addr):
		NetService.__init__(self,name,addr)
	
	def eventConnCreated(self,conn):
		NetService.eventConnCreated(self,conn)
		#print 'client connection created!',conn
		thread = NetConnThread(conn)
		
	def eventGotMessage(self,msglist,conn):
		for m in msglist:
			print m.attrs,m.bin
		
test_dest = ('localhost',12004)

class MyClient:
	def __init__(self):
		conn = NetConnection(recvfunc = self.recvEvent)
		r = conn.connect( test_dest)
		thread = NetConnThread(conn)
		for n in range(100):
			if not conn.sendMessage(MsgCallReturn(value=[n],bin='A'*(n+1) )):
				print 'serivce lost ... abord!!'
				break
			time.sleep(1)
			
	def recvEvent(self,evt):
		evt.conn == 1
		if evt.type == NetConnectionEvent.EVENT_DATA:
			for m in evt.data:
				print m.attrs,m.bin
		if evt.type == NetConnectionEvent.EVENT_DISCONNECTED:
			print 'connection lost!'
			
def test_service():
	server = NetworkServer('test-server')
	svc =MyService('fileserver',test_dest)
	#svc = server.createService("filesync-server",'localhost',12001,MyService)
	server.addService(svc)
	svc.start()
	#time.sleep(5)
	#svc.shutdown()

def test_client():
	MyClient()
	
if __name__=='__main__':
	#test_packetqueue()
	p = sys.argv[1]
	if p=='client':
		test_client()
		sys.exit(0)
	if p=='service':
		test_service()
		
	time.sleep(100)