#--coding:utf-8--
from django.db import models

from datetime import datetime

MAXLEN_TINY= 30
MAXLEN_TINY2 = 50
MAXLEN_SHORT= 80
MAXLEN_SHORT2= 160
MAXLEN_NORMAL = 240
MAXLEN_MEDIUM = 320
MAXLEN_LONG = 480


#录音文件数据表
class AudioFile(models.Model):
	digest =  models.CharField(max_length=MAXLEN_SHORT,db_index=True)       #spx文件md5摘要
	spxfile = models.CharField(max_length=MAXLEN_TINY,db_index=True)        #spx文件名称（带路径)
	filetime = models.IntegerField(db_index = True)                         #文件时间
	duration = models.IntegerField(db_index = True )                        #录音时长
	status = models.IntegerField(db_index= True)                            #0 - 未上传; 1 - 已上传
	uptime = models.IntegerField(db_index= True)                            #上传时间
	serial  = models.IntegerField(db_index= True)                           #索引编号
	attr = models.IntegerField(db_index=True)                               # 来去电属性，0：来电；1：去电 2：录音 3:未接
	phone = models.CharField(max_length=30,db_index=True)                   #电话号码
	client_sid = models.CharField(max_length=40,db_index=True,null=True)    #客户编号
	memo = models.TextField(null=True,db_index=True)                        #备注
	memo_status = models.IntegerField(db_index= True)                       #0 - 未上传; 1 - 已上传, 备注信息在被修改之后，状态重置为0，等待下次更新
	type = models.IntegerField(db_index=True)                     			#类型  1 - 常规 ；2 - 通话 ； 99 -其他
	productid = models.CharField(max_length=40,null=True,db_index=True)     #产品ID号
	operator = models.CharField(max_length=40,null=True,db_index=True)      #录入操作者名称

class Client(models.Model):
	sid = models.CharField(max_length=40,db_index=True)                 #客户编号
	name = models.CharField(max_length=40,db_index=True)                #客户名称
	sex = models.IntegerField()                                         #性别
	corp = models.CharField(max_length=40,null=True)                    #公司
	phone1 = models.CharField(max_length=30,null=True,db_index=True)    #电话1
	phone2 = models.CharField(max_length=30,null=True,db_index=True)    #电话2

	address = models.CharField(max_length=100,null=True,db_index=True)  #地址
	postcode = models.CharField(max_length=20,null=True)                #邮政编码
	email = models.CharField(max_length=40,null=True,db_index=True)     #邮件地址
	website = models.CharField(max_length=40,null=True,db_index=True)   #网站地址
	im = models.CharField(max_length=60,null=True,db_index=True)        #qq/msn
	memo = models.TextField(null=True,db_index=True)                    #附加说明                         #备注
	personid = models.CharField(max_length=40,null=True,db_index=True) 	#身份证号码
	clientid = models.CharField(max_length=40,null=True,db_index=True) 	#客户ID号
	pinyin =  models.CharField(max_length=40,null=True,db_index=True) 	#客户拼音
	status = models.IntegerField(db_index= True)                        #0 - 未上传; 1 - 已上传
	phone3 = models.CharField(max_length=30,null=True,db_index=True)    #电话3 #2013.5.24 added
	owner_org = models.CharField(max_length=60,null=True,db_index=True) 	#客户归属信息 input: text   added 2013.5.24
	type = models.IntegerField(default=0,db_index=True)      #客户类型 input: list       2013.5.24
			#CLIENT_TYPES={0:u'普通客户',1:u'沃德客户',
			#			2:u'交银客户',3:u'私人银行'
			#				}
	custom_tag = models.CharField(max_length=60,null=True,db_index=True)  #自定义标签 2013.11.8
#

class SysSettings(models.Model):
	key = models.CharField(max_length=80,db_index=True)
	value = models.TextField(null=True)
	memo = models.TextField(null=True)

#临时录音文件存放
class AudioTemp(models.Model):
	serial  = models.IntegerField(db_index= True)  #录音文件索引
	client_sid = models.CharField(max_length=40,db_index=True,null=True)
	memo = models.TextField(null=True)
	type = models.CharField(max_length=30,null=True)          #类型
	productid = models.CharField(max_length=40,null=True)     #产品ID号#
	operator = models.CharField(max_length=40,null=True)      #录入操作者名称



#录音文件对应多个客户,临时表
class AudioMapClient(models.Model):
	digest = models.CharField(max_length=40,db_index=True)
	filetime = models.IntegerField(db_index = True)
