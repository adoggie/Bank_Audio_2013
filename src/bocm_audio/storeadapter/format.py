# -*- coding: utf-8 -*-

#spx转换成mp3

import sys,os,os.path,time,struct,traceback,threading,datetime,struct,array,sqlite3
import  pickle,hashlib,base64

#'''
#文件的前面32个Bytes是头，剩下的都是数据，每20个Bytes是一个speex数据包；
#
#{
#    unsigned short IndexNo;   //序号
#
#    unsigned char  Attribute: 2 ; //来去电属性，0：来电；1：去电 2：录音 3:未接
#    unsigned char  DeleteStatus: 1 ;   //这个你不用关心；//1：正常，0：曾经后一条被删除，上电需地址跳跃
#    unsigned char  Reserve: 1 ;        //这个你不用关心；//长度补全标记
#    unsigned char  Month: 4 ;   //月份
#
#    unsigned short Day: 5 ;     //日期
#    unsigned short Hour: 5 ;    //小时
#    unsigned short Minute: 6 ;   //分钟
#
#    //移到最后unsigned char  Number[6] ;  //电话号码，每4bit存一个号码，共12号码，Number[0]低4bit为第一个号码，高4bit为第二个号码，类推。0xFF表示为无效号码或表示号码结束。
#
#	unsigned long  FileBeginAddr;   //文件起始位置，删至3个byte，因为原来最后一个byte肯定是0
#
#	unsigned long  Filelength;   //文件长度，单位byte，删至2个byte，因为原来最后一个byte肯定是0，最高一个byte删除，这样一个录音文件最长只能4.6小时，chenzhm
#    unsigned char  Number[10] ;  //电话号码，每4bit存一个号码，共20号码，Number[0]低4bit为第一个号码，高4bit为第二个号码，类推。0xFF表示为无效号码或表示号码结束。
#    unsigned long  LSerialNumber;//电话录音的唯一号。第20个字节开始
#    unsigned char  Year;             //电话记录的年份信息。第24个字节
#}FileInfo;
#'''


class SpxFileInfo:
	def __init__(self):
		self.index = 0
		self.attr = 0
		self.deletestatus= 0
		self.reserve = 0
		self.month = 0
		self.day = 0
		self.hour = 0
		self.minute = 0
		self.fileaddr = 0
		self.filelen = 0
		self.phone=''
		self.serial = 0
		self.year = 0
		self.duration=0
		self.second = 0

	def filename(self):
		padnum = 20 - len(self.phone)

		phone = 'x'*padnum+self.phone
		phone = phone.replace('*','x')
		return '%04d%02d%02d_%02d%02d%02d_%s_%08d_%s'%(self.year,self.month,self.day,
		                                         self.hour,self.minute,self.second,
		                                         phone,self.serial,self.attr)
		# 2013.10.7 增加录音秒规格

	def createtime(self):
		return datetime.datetime(self.year,self.month,self.day,self.hour,self.minute,self.second)

#spx文件头32字节大小 ,最后一个s[24:28]为year

def parseSpxFileInfo(spxfile):
	try:
		spx = SpxFileInfo()
		f = open(spxfile,'rb')
		s = f.read(40)
		f.close()
		return parseSpxFileInfoByStream(s)
	except:
		return None

def __parseSpxFileInfo(spxfile):
	try:
		spx = SpxFileInfo()
		f = open(spxfile,'rb')
		s = f.read(40)
		f.close()
		p = 0
		set = 0
		index,set = struct.unpack('!HB',s[p:p+3])
		p+=3
#		print bin(set)
		attr = set >>6
		month = set&0xf
		set, = struct.unpack('!H',s[p:p+2])
		p+=2
		day = set>>11
		hour = (set>>6)&(0b11111)
		minute = set&(0b111111)

		fileaddr, = struct.unpack('!I',s[p:p+4])
		p+=4
#		filelen, = struct.unpack('!I',s[p:p+4])
#		p+=4
		#文档里面写的FileLength有错误, 长度只能为1
		p+=1
		numbers = struct.unpack('BBBBBBBBBB',s[p:p+10])
		p+=10
		phone = ''
#		print len(numbers)
		for b in numbers:
			print b&0xf,b>>4&0xf
			if b == 0xff :
				break

			if b>>4&0xf == 0xf:
				break
			phone+= chr(ord('0')+((b>>4)&0xf))

			if b&0xf == 0xf:
				break
			phone+= chr(ord('0')+(b&0xf))


		serial, = struct.unpack('!I',s[20:24])
		year, = struct.unpack('B',s[24:25])
		year+=2000
		# print attr,year,month,day,hour,minute,hex(serial),phone

		spx.index = index
		spx.serial = serial
		spx.attr = attr
		spx.year = year
		spx.month = month
		spx.day = day
		spx.hour = hour
		spx.minute = minute
		spx.phone = phone
		# spx.fileaddr = fileaddr
		# spx.filelen = filelen
		return spx
	except:
		traceback.print_exc()
		return None



def parseSpxFileInfoByStream(hdr):
	try:
		s = hdr
		spx = SpxFileInfo()
		p = 0
		set = 0
		index,set = struct.unpack('!HB',s[p:p+3])
		p+=3
		attr = set >>6
		month = set&0xf
		set, = struct.unpack('!H',s[p:p+2])
		p+=2
		day = set>>11
		hour = (set>>6)&(0b11111)
		minute = set&(0b111111)
		#fieladdr - 3 bytes 最高8bit需补0
		val = s[p:p+3] + '\x00'
		fileaddr, = struct.unpack('!I',val)
		p+=3
		filelen, = struct.unpack('!H',s[p:p+2])
		filelen = filelen << 8
		p+=2
		#文档里面写的FileLength有错误, 长度只能为1

		numbers = struct.unpack('BBBBBBBBBB',s[p:p+10])
		p+=10
		phone = ''
#		print len(numbers)
		for b in numbers:
			# print b&0xf,b>>4&0xf
			if b == 0xff :
				break

			if b>>4&0xf == 0xf:
				break
			phone+= chr(ord('0')+((b>>4)&0xf))

			if b&0xf == 0xf:
				break
			phone+= chr(ord('0')+(b&0xf))

		#非数字拨号键以#显示 2013.7.8
		line = ''
		for c in phone:
			if c in ('0','1','2','3','4','5','6','7','8','9'):
				pass
			elif c ==':':
				c = '*'
			elif c == ';':
				c = '#'
			else:
				c = '#'
			line+= c
		phone = line
		#----

		serial, = struct.unpack('!I',s[20:24])
		year, = struct.unpack('B',s[24:25])
		year+=2000
		second, = struct.unpack('B',s[25])  # second 2013.10.7

		spx.index = index
		spx.serial = serial
		spx.attr = attr
		spx.year = year
		spx.month = month
		spx.day = day
		spx.hour = hour
		spx.minute = minute
		spx.phone = phone
		spx.fileaddr = fileaddr
		spx.filelen = filelen
		spx.duration = int(filelen/1000)
		spx.second = second
		# print index,serial,attr,year,month,day,hour,minute,phone,hex(fileaddr),hex(filelen),spx.duration
		return spx

		# 1k = 1s
	except:
		traceback.print_exc()
		return None


if __name__ == '__main__':
	parseSpxFileInfo(r'c:\201104101626_000907_xxxxxxxx913386108100.spx')
	parseSpxFileInfo(r'c:\201104240855_000920_xxxxxxxxxxxx31198606.spx')
	parseSpxFileInfo(r'C:\leadtel\media\201107031113_001040_xxxxxxx9013941156669.spx')


