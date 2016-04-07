#--coding:utf-8--
from django.db import models
from django.utils.encoding import force_unicode,smart_unicode
import traceback

MAXLEN_TINY= 30
MAXLEN_TINY2 = 50
MAXLEN_SHORT= 80
MAXLEN_SHORT2= 160
MAXLEN_NORMAL = 240
MAXLEN_MEDIUM = 320
MAXLEN_LONG = 480

class DescendantOrganizationManager(models.Manager):
	def get_query_set(self):
		return super(DescendantOrganizationManager, self).get_query_set()

#机构组织表， 树形结构
class Organization(models.Model):
	"""Organization"""
	name = models.CharField(max_length=MAXLEN_SHORT)
	parent = models.ForeignKey('Organization',related_name='suborg_set',null=True,db_index=True) #,on_delete=models.PROTECT)
	phone = models.CharField(max_length=20,null=True,default='')   #电话
	address = models.CharField(max_length=200,null=True,default='')    #地址
	memo = models.TextField(null=True,default='')  #组织机构说明
	org_sid = models.CharField(max_length=30,null=True,default='',db_index=True)   #组织机构编号 2013.10.8
	link = models.CharField(max_length=MAXLEN_MEDIUM,default='') #记录方式 parentlink+id+_ 表示机构之间的父子关系
	objects = DescendantOrganizationManager()
	class Meta:
		db_table = 'audio_organization'

	def __unicode__(self):
		return self.name

#系统管理人员
class DescendantUserManager(models.Manager):
	def get_query_set(self):
		return super(DescendantUserManager, self).get_query_set()

class User(models.Model):
	org = models.ForeignKey('Organization',on_delete=models.PROTECT)                     #隶属的机构
	user = models.CharField(max_length=40,unique=True,db_index=True)        #用户登陆名
	passwd = models.CharField(max_length=20,db_index=True)      #登陆密码
	name = models.CharField(max_length=40,null=True,db_index=True,default='')  #用户名称
	phone = models.CharField(max_length=30,null=True,default='')           #电话
	address=models.CharField(max_length=120,null=True,default='')          #地址
	email = models.CharField(max_length=40,null=True,default='')           #邮件地址
	rights = models.IntegerField()                   #权限掩码

	objects = DescendantUserManager()

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

#系统管理人员
class DescendantTerminalManager(models.Manager):
	def get_query_set(self):
		return super(DescendantTerminalManager, self).get_query_set()

#语音终端设备
class Terminal(models.Model):
	OFFLINE=0
	ONLINE=1
	STATUS_CHOICES=(
		(OFFLINE,u"未上线"),
		(ONLINE,u"在线")
	)
	org = models.ForeignKey('Organization',on_delete=models.PROTECT)             #设备隶属于那个分支机构
	user = models.CharField(max_length=40,unique=True,db_index=True)               #话机编号
	passwd = models.CharField(max_length=20,db_index=True)                   #电话号码
	address = models.CharField(max_length=160,null=True,default='')
	phone = models.CharField(max_length=30,null=True,db_index=True,default='')                 #联系电话
	postcode = models.CharField(max_length=20,null=True,default='')          #地址
	employee = models.CharField(max_length=20,null=True,db_index=True,default='')          #员工名称
	addition = models.TextField(null=True,default='')              #附属信息
	creator = models.ForeignKey('User')                 #创建者
	createtime = models.DateTimeField(db_index=True)    #创建时间
	status = models.IntegerField(default=0,choices=STATUS_CHOICES)             #状态 0 - 未上线 ； 1 -在线
	regtime = models.DateTimeField(null=True)                    #最近一次登录时间
	appver = models.CharField(max_length=20,default='')     #终端侧软件版本

	objects = DescendantTerminalManager()
	def __unicode__(self):
		return self.user

	class Meta:
		db_table = 'audio_terminal'

#录音资料
class Archive(models.Model):
	LAIDIAN_ATTR=0
	QUDIAN_ATTR=1
	LUYIN_ATTR=2
	WEIJIE_ATTR =3
	ATTR_CHOICES=(
		(LAIDIAN_ATTR,u"来电"),
		(QUDIAN_ATTR,u"去电"),
		(LUYIN_ATTR,u"录音"),
		(WEIJIE_ATTR,u"未接")
	)
	PUTONG_TYPE=1
	XIAOSHOU_TYPE=2
	QITA_TYPE=99
	TYPE_CHOICES=(
		(PUTONG_TYPE,u"日常沟通"),
		(XIAOSHOU_TYPE,u"销售"),
		(QITA_TYPE,u"其他"),
	)
	term = models.ForeignKey('Terminal',on_delete=models.PROTECT)                    #终端设备
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
	attr = models.IntegerField(choices=ATTR_CHOICES)                #来去电属性，0：来电；1：去电 2：录音 3:未接
	serial = models.IntegerField()              #电话录音的唯一号。第20个字节开始
	memo = models.TextField(null=True,db_index=True,default='')
	client = models.ForeignKey('Client',null=True,on_delete=models.SET_NULL)
	type = models.IntegerField(db_index=True,default=1,choices=TYPE_CHOICES)          #通话类型 1 - 普通 ; 2 - 销售 ; 99 - 其他

	productid = models.CharField(max_length=40,null=True,db_index=True,default='')     #产品ID号
	url = models.CharField(max_length=240,null=True,default='')     #url 不包括主机和端口，例如 /medias/first/2013-5-20/012010212012.mp3
	client_sid = models.CharField(max_length=40,db_index=True,null=True,default='')   # added soctt 2013.6.10 ,
	# 用于同步语音备注与客户信息关联使用，web开发者不用关心
	operator = models.CharField(max_length=40,null=True,db_index=True)      #录入操作者名称

	def __unicode__(self):
		return self.name

	class Meta:
		db_table = 'audio_archive'
		ordering = ['-rectime','-serial']

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
	MAN=1
	WOMEN=0
	SEX_CHOICES=(
		(MAN,u"男"),
		(WOMEN,u"女")
	)
	PUTONG_CLIENT=0
	WODE_CLIENT=2
	JIAOTONG_CLIENT=1
	SIREN_CLIENT =3
	TYPE_CHOICES=(
		(PUTONG_CLIENT,u"普通客户"),
		(WODE_CLIENT,u"沃德客户"),
		(JIAOTONG_CLIENT,u"交银客户"),
		(SIREN_CLIENT,u"私人银行")
	)
	term = models.ForeignKey('Terminal',on_delete=models.PROTECT)                                #客户信息隶属于话机账号
	sid = models.CharField(max_length=40,db_index=True)                 #表记录编号，无需显示
	name = models.CharField(max_length=40,db_index=True)                #客户名称
	sex = models.IntegerField(choices=SEX_CHOICES)                                         #性别 1男 2 女
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
	type = models.IntegerField(default=0,db_index=True,choices=TYPE_CHOICES)      #客户类型 input: list       2013.5.24
						#  0:u'普通客户',1:u'沃德客户',2:u'交银客户',3:u'私人银行'
	custom_tag = models.CharField(max_length=60,null=True,db_index=True,default='')  #自定义标签 2013.11.8
	def __unicode__(self):
		return self.name

	class Meta:
		db_table = 'audio_client'
		ordering = ['pinyin']

#用户登陆日志表
class LoginLog(models.Model):
	time = models.DateTimeField(db_index=True)              #登陆时间
	user = models.CharField(max_length=40,db_index=True)    #登陆用户名
	ip = models.TextField(max_length=40,db_index=True)      #登陆ip

	class Meta:
		db_table = 'audio_loginlog'


#用户行为操作日志表
class UserLogManager(models.Manager):
	def log_action(self, request,type,target_type,target=None,newtarget=None,change_message=''):
		user = force_unicode(request.session.get("user"))
		opt_value_dict = dict(self.model.OPT_CHOICES)
		target_type_dict = dict(self.model.TARGET_TYPE_CHOICES)
		if not change_message:
			change_message = u'"'+user+u'"用户'+opt_value_dict[type]+u"了"+target_type_dict[target_type]
			if target:
				target = force_unicode(target)
				change_message+=u'"'+smart_unicode(target)+u'"'
			if newtarget:
				change_message+=u'为"'+smart_unicode(newtarget)+u'"'
		e = self.model(user=user,type=type,target=target,target_type=target_type,detail=change_message)
		e.save()

class UserLog(models.Model):
	ADD_OPT=1
	DELE_OPT=2
	EDIT_OPT =3
	GRANT_OPT =4
	PLAY_OPT =5
	DOWN_OPT=6
	EXPORT_OPT=7
	DELEMANY_OPT = 8
	OPT_CHOICES=(
		(ADD_OPT,u"添加"),
		(DELE_OPT,u"删除"),
		(EDIT_OPT,u"修改"),
		(GRANT_OPT,u"授权"),
		(PLAY_OPT,u"播放"),
		(DOWN_OPT,u"下载"),
		(EXPORT_OPT,u"导出"),
		(DELEMANY_OPT,u"批量删除了"),
	)
	ORG = 1
	USER = 2
	TERM = 3
	CLIENT = 4
	ARCH = 5
	TARGET_TYPE_CHOICES = (
		(ORG,u"机构"),
		(USER,u"系统用户"),
		(TERM,u"终端设备"),
		(CLIENT,u"客户信息"),
		(ARCH,u"语音资料"),
	)

	time = models.DateTimeField(db_index=True,auto_now_add=True)                  #操作时间
	user = models.CharField(max_length=40,db_index=True)        #用户名
	type = models.IntegerField(db_index=True,choices=OPT_CHOICES)                   #操作类型 1 - 添加; 2 - 删除 ; 3 - 修改 ； 4 - 授权 ； 5 - 播放 ； 6 - 下载 ;7-导出
	target = models.CharField(max_length=140,db_index=True,null=True)      #操作对象
	target_type = models.IntegerField(db_index=True,choices =TARGET_TYPE_CHOICES)            #  1- 机构 ； 2 - 系统用户 ； 3 - 终端设备 ； 4 - 客户信息； 5 - 语音资料
	detail = models.TextField(null=True,default='')             #操作描述文本

	objects = UserLogManager()

	class Meta:
		db_table = 'audio_userlog'
