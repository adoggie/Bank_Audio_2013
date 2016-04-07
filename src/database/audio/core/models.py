#--coding:utf-8--
from django.db import models

from datetime import datetime
import traceback

MAXLEN_TINY= 30
MAXLEN_TINY2 = 50
MAXLEN_SHORT= 80
MAXLEN_SHORT2= 160
MAXLEN_NORMAL = 240
MAXLEN_MEDIUM = 320
MAXLEN_LONG = 480

#机构组织表， 树形结构
class Organization(models.Model):
	name = models.CharField(max_length=MAXLEN_SHORT)
	parent = models.ForeignKey('Organization',related_name='suborg_set',null=True,db_index=True)
	phone = models.CharField(max_length=20,null=True,default='')   #电话
	address = models.CharField(max_length=200,null=True,default='')    #地址
	memo = models.TextField(null=True,default='')  #组织机构说明
	link = models.CharField(max_length=MAXLEN_MEDIUM,default='') #记录方式 parentlink+id+_ 表示机构之间的父子关系

	class Meta:
		db_table = 'audio_organization'

	def __unicode__(self):
		return self.name

#系统管理人员
class User(models.Model):
	org = models.ForeignKey('Organization')                     #隶属的机构
	user = models.CharField(max_length=40,db_index=True)        #用户登陆名
	passwd = models.CharField(max_length=20,db_index=True)      #登陆密码
	name = models.CharField(max_length=40,null=True,db_index=True,default='')  #用户名称
	phone = models.CharField(max_length=30,null=True,default='')           #电话
	address=models.CharField(max_length=120,null=True,default='')          #地址
	email = models.CharField(max_length=40,null=True,default='')           #邮件地址
	rights = models.IntegerField()                   #权限掩码

	def __unicode__(self):
		return self.user

	class Meta:
		db_table = 'audio_user'

	def has_permission(self,type,id):
		try:
			if type>0 and type<6 and id:
				parent_org = self.org
				tree_node_org = TreeNode.objects.get(type=1,obj_id=parent_org.id)
				tree_node_childorg = TreeNode.objects.filter(link__startswith=tree_node_org.link,type=1)
				child_org_ids=[]
				for tree_node in tree_node_childorg:
					child_org_ids.append(tree_node.obj_id)
				self.child_org_ids = child_org_ids
				if type==1:
					organization = Organization.objects.get(id=id)
					belong_org_id = organization.id
				elif type==2:
					user = User.objects.get(id=id)
					belong_org_id = user.org.id
				elif type==3:
					terminal = Terminal.objects.get(id=id)
					belong_org_id = terminal.org.id
				elif type == 4:
					client = Client.objects.get(id=id)
					belong_org_id = client.term.org.id
				elif type ==5:
					archive = Archive.objects.get(id=id)
					belong_org_id = archive.term.org.id
				else:
					belong_org_id=0
				if belong_org_id >0:
					return (belong_org_id in child_org_ids)
			else:
				return False
		except Exception,e:
			traceback.print_exc()
			return False

#语音终端设备
class Terminal(models.Model):
	org = models.ForeignKey('Organization')             #设备隶属于那个分支机构
	user = models.CharField(max_length=40,db_index=True)               #话机编号
	passwd = models.CharField(max_length=20,db_index=True)                   #电话号码
	address = models.CharField(max_length=160,null=True,default='')
	phone = models.CharField(max_length=30,null=True,db_index=True,default='')                 #联系电话
	postcode = models.CharField(max_length=20,null=True,default='')          #地址
	employee = models.CharField(max_length=20,null=True,db_index=True,default='')          #员工名称
	addition = models.TextField(null=True,default='')              #附属信息
	creator = models.ForeignKey('User')                 #创建者
	createtime = models.DateTimeField(db_index=True)    #创建时间
	status = models.IntegerField(default=0)             #状态 0 - 未上线 ； 1 -在线
	regtime = models.DateTimeField(null=True)                    #最近一次登录时间
	def __unicode__(self):
		return self.user

	class Meta:
		db_table = 'audio_terminal'

#录音资料
class Archive(models.Model):
	term = models.ForeignKey('Terminal')                    #终端设备
	digest= models.CharField(max_length=40,db_index=True)   #mp3文件md5
	spx_digest= models.CharField(max_length=40,db_index=True)   #spx文件md5
	phone = models.CharField(max_length=40,db_index=True)   #电话
	name = models.CharField(max_length=80,db_index=True)    #文件名称
	path = models.CharField(max_length=200,db_index=True)   #存储路径

	size = models.IntegerField()                            #文件大小
	rectime = models.DateTimeField()                           #录音时间
	duration = models.IntegerField()                        #时长
	uptime = models.DateTimeField()                         #上传时间

	index = models.IntegerField()               #序号
	attr = models.IntegerField()                #来去电属性，0：来电；1：去电 2：录音 3:未接
	serial = models.IntegerField()              #电话录音的唯一号。第20个字节开始
	memo = models.TextField(null=True,db_index=True,default='')
	client = models.ForeignKey('Client',null=True)
	type = models.IntegerField(db_index=True,default=1)          #通话类型 1 - 普通 ; 2 - 销售 ; 99 - 其他

	productid = models.CharField(max_length=40,null=True,db_index=True,default='')     #产品ID号
	url = models.CharField(max_length=240,null=True,default='')     #url 不包括主机和端口，例如 /medias/first/2013-5-20/012010212012.mp3
	client_sid = models.CharField(max_length=40,db_index=True,default='')   # added soctt 2013.6.10 , 用于同步语音备注与客户信息关联使用，web开发者不用关心

	def __unicode__(self):
		return self.name

	class Meta:
		db_table = 'audio_archive'

class TreeNode(models.Model):
	parent = models.ForeignKey("self", blank=True, null=True, related_name="children")
	name = models.CharField(max_length=MAXLEN_SHORT)
	type = models.IntegerField() #结点类型,1表示Organization,2表示User,3表示Terminal,4表示
	obj_id = models.IntegerField()
	level = models.IntegerField() #表示结点所在整个树的层次
	link = models.CharField(max_length=MAXLEN_MEDIUM) #记录方式 parentlink+id+_ 此字段备用

	def __unicode__(self):
		return self.name

	class Meta:
		db_table = 'audio_treenode'




#系统全局参数配置
class SysSettings(models.Model):
	key = models.CharField(max_length=80,db_index=True)
	value = models.TextField(null=True)
	memo = models.TextField(null=True)
	class Meta:
		db_table = 'audio_syssettings'

#终端话机相关的客户信息表
class Client(models.Model):
	term = models.ForeignKey('Terminal')                                #客户信息隶属于话机账号
	sid = models.CharField(max_length=40,db_index=True)                 #客户编号
	name = models.CharField(max_length=40,db_index=True)                #客户名称
	sex = models.IntegerField()                                         #性别 1男 2 女
	corp = models.CharField(max_length=40,null=True,default='')                    #公司
	phone1 = models.CharField(max_length=30,null=True,db_index=True,default='')    #电话1
	phone2 = models.CharField(max_length=30,null=True,db_index=True,default='')    #电话2
	address = models.CharField(max_length=100,null=True,db_index=True,default='')  #地址
	postcode = models.CharField(max_length=20,null=True,default='')                #邮政编码
	email = models.CharField(max_length=40,null=True,db_index=True,default='')     #邮件地址
	website = models.CharField(max_length=40,null=True,db_index=True,default='')   #网站地址
	im = models.CharField(max_length=60,null=True,db_index=True,default='')        #qq/msn
	memo = models.TextField(null=True,db_index=True,default='')
	personid = models.CharField(max_length=40,null=True,db_index=True,default='') #身份证号码
	clientid = models.CharField(max_length=40,null=True,db_index=True,default='') #客户ID号
	pinyin =  models.CharField(max_length=40,null=True,db_index=True,default='') 	#客户拼音
	phone3 = models.CharField(max_length=30,null=True,db_index=True,default='')    #电话3 #2013.5.24 added
	owner_org = models.CharField(max_length=60,null=True,db_index=True,default='') 	#客户归属信息 input: text   added 2013.5.24
	type = models.IntegerField(default=0,db_index=True)      #客户类型 input: list       2013.5.24
						#  0:u'普通客户',1:u'沃德客户',2:u'交银客户',3:u'私人银行'
	def __unicode__(self):
		return self.sid

	class Meta:
		db_table = 'audio_client'