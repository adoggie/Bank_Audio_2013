# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib

import message
from message import *

class MsgImagePut_SelectNodeRequest(MessageBase):
	def __init__(self,space):
		MessageBase.__init__(self,'imageput_selectnode_req')
		self.attrs['needspace']=space
		
class MsgImagePut_SelectNodeResponse(MessageBase):
	def __init__(self,nodeserver=(),msg=''):
		MessageBase.__init__(self,'imageput_selectnode_resp')
		self.attrs['nodeserver']=nodeserver #(host,port)
		self.attrs['errmsg']=msg

		
#node server 上报状态信息
class MsgManagement_NodeStatus(MessageBase):
	def __init__(self,status):
		MessageBase.__init__(self,'mgr_nodestatus')
		self.attrs['nodestatus']=status
				
'''
			zone{
				'maxspace':self.maxspace,
				'freespace':self.freespace,
				'id':self.id,
				'path':self.path,
				'tempdir':self.tempdir,
				'lowater':self.lowater
				}


	status = {
			"id":self.id,
			'filesvc': (self.conf['ipaddr_filesvc'],self.conf['port_filesvc']),
			'mediasvc': (self.conf['ipaddr_mediasvc'],self.conf['port_mediasvc']),
			'zones':[]
		}
		for z in self.zones:
			status['zones'].append(z.hash_status())

'''


#查询路网影像
class MsgMgr_QueryNetworkImage(MessageBase):
	def __init__(self):
		MessageBase.__init__(self,'mgr_query_networkimage')
		self.attrs['georect']=() 		#地理区界 x,y,w,h
		self.attrs['starttime']=0
		self.attrs['endtime']=0
		self.attrs['daystarthour'] =0 	#一天开始时间 hours
		self.attrs['dayendhour'] = 0  	#一天结束时间 hours
		self.attrs['limit'] = 100		#接收记录数上限
		self.attrs['taskid'] = 0 		#计划任务编号
		

class ImageRecord_t:
	
	def __init__(self):
		self.id = 0 	#数据库记录编号
		self.imageid=''
		self.starttime = 0		#开始时间
		self.duration	= 0 	#时长
		self.nodeid = ''	#存储nodeserver服务地址(host,port)
		self.nodesvc=()		#服务主机和端口
		self.gpsdata =[]		#gps点集合
		self.wkt = []				#WKT格式的点集合
		self.roads=[]			#轨迹行驶过的路段		
		self.filesize=0
		self.digest=''
		self.tagnum = 0			#标记数量
		self.taskname='--'
		self.tags=[]
		# roads = [{first:{roadid,messid,point},second:{roadid,messid,pint}},...]
		
class MsgMgr_QueryResultNetworkImage(MessageBase):
	def __init__(self):
		MessageBase.__init__(self,'mgr_queryresult_networkimage')
		self.attrs['georect']=()
		self.attrs['starttime']=0
		self.attrs['endtime']=0
		self.attrs['daystarthour'] =0 	#一天开始时间
		self.attrs['dayendhour'] = 0  	#一天结束时间
		self.attrs['limit'] = 100		#接收记录数上限
		self.attrs['results']=[]		#[ImageRecord_t(),..]


if __name__=='__main__':
	import utils
	print utils.hashobject(ImageRecord_t())































