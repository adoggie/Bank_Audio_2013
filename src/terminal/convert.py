# -*- coding: utf-8 -*-

#spx转换成mp3
#
# spx文件被添加了私有的头部信息，并且没有加上标准的ogg/speex头信息，导致外部程序无法读取访问
# 应该添加上ogg/speex头信息便可

# - spx转换为mp3，将spx头部信息添加到mp3尾部
# mp3 格式
#   文件尾部保留100字节，
#   leadtel - 8 bytes   magic
#   (phone,filename,createtime,duration)  encode json array
#

import sys,os,os.path,time,struct,traceback,threading,datetime,struct,array,sqlite3
import  pickle,hashlib,base64,shutil,subprocess

from base import *
import format
import utils
	
def pack_fileinfo(mp3):
	pass
	
TEMPDIR = 'c:/temp/audio'
CODEC_BLOCK_SIZE = 500*2*30
#CODEC_BLOCK_SIZE = 500

def spx_convert_mp3(spxfile,mp3file,subfix=''):
	TEMPDIR = getApp().getTempPath()


	riffhdr = [0x4952,0x4646,0x3EA4,0x0,0x4157,0x4556,0x6D66,0x2074,
		0x0010,0x0,0x1,0x1,0x1F40,0x0,0x3E80,0x0,
		0x2,0x10,0x6164,0x6174,0x0,0x0]

	print spxfile
	f = open(spxfile,'rb')
	d = f.read()
	f.close()
	hdrsize = 32 
	magic,= struct.unpack('I',d[28:28+4])
	if magic !=  0xffffffff:
		hdrsize = 19
#	hdrsize = 32
	print 'hdrsize:',hdrsize

	npos = hdrsize 
	wavlen = int((len(d) - hdrsize)/500)
	wavlen*=8000
	riffhdr[21] = (wavlen >> 16) & 0xffff
	riffhdr[20] = wavlen & 0xffff
	riffhdr[3] = ((wavlen+36)>>16)& 0xffff
	riffhdr[2] =  (wavlen+36) & 0xffff

	if not os.path.exists(TEMPDIR):
		os.mkdir(TEMPDIR)
	segfile = TEMPDIR +'/tempseg.dat'+subfix
	pcmfile = TEMPDIR +'/temppcm.dat'+subfix
	pcmbytes=''
	while True:
		block = d[npos:npos+CODEC_BLOCK_SIZE]
		if not block:
			break
		npos+=CODEC_BLOCK_SIZE
		f = open(segfile,'wb')
		f.write(block)
		f.close()
#		print '--'*20
#		print segfile,pcmfile
		segfile = os.path.normpath(segfile)
		pcmfile = os.path.normpath(pcmfile)
		cmd = u'speex.exe "%s" "%s"'%(segfile,pcmfile)
#		print cmd.encode('gbk')
		# r = os.system(cmd.encode('gbk'))
		r = subprocess.call(cmd.encode('gbk'),shell=True)
		if r :
			print 'speex fail!'
			return ''
		f = open(pcmfile,'rb')
		pcmbytes+=f.read()
		print len(pcmbytes)
		f.close()
	pcmfile = spxfile.replace('.spx','.pcm')
	print 'spx to pcm completed! >> ',pcmfile
	f = open(pcmfile,'wb')
	f.write(pcmbytes)
	f.close()
	print 'preparing pcm to wav ..'
	wavfile = spxfile.replace('.spx','.wav')
	f = open(wavfile,'wb')
	for n in riffhdr:
		f.write( struct.pack('H',n))
	f.write(pcmbytes)
	f.close()
	#-- copy wav to $app/temp/spx-digest.wav
	if getApp().getSystemConfig('retain_wav_to_temp','0') == '1':
		try:#检测是否已经存在对应的 wav文件了
			digest = utils.getfiledigest(spxfile)
			destpath = os.path.join(getApp().getTempPath(),digest+'.wav')
			if not os.path.exists(destpath):
				shutil.copyfile(wavfile,destpath)
		except:
			traceback.print_exc()
	#-- end ----
	mp3file = TEMPDIR +'/audiofinal.mp3'
	if not wav_to_mp3(spxfile,wavfile,mp3file):
		return ''
	os.remove(pcmfile)
	os.remove(wavfile)
	return mp3file

#	print 'pcm data size:',len(pcmbytes)


def spx_convert_wav(spxfile,wavfile,subfix=''):
	TEMPDIR = getApp().getTempPath()

	riffhdr = [0x4952,0x4646,0x3EA4,0x0,0x4157,0x4556,0x6D66,0x2074,
		0x0010,0x0,0x1,0x1,0x1F40,0x0,0x3E80,0x0,
		0x2,0x10,0x6164,0x6174,0x0,0x0]
	f = open(spxfile,'rb')
	d = f.read()
	f.close()
	hdrsize = 32
	magic,= struct.unpack('I',d[28:28+4])
	if magic !=  0xffffffff:
		hdrsize = 19
#	hdrsize = 32
	print 'hdrsize:',hdrsize

	npos = hdrsize
	wavlen = int((len(d) - hdrsize)/500)
	wavlen*=8000
	riffhdr[21] = (wavlen >> 16) & 0xffff
	riffhdr[20] = wavlen & 0xffff
	riffhdr[3] = ((wavlen+36)>>16)& 0xffff
	riffhdr[2] =  (wavlen+36) & 0xffff

	if not os.path.exists(TEMPDIR):
		os.mkdir(TEMPDIR)
	segfile = TEMPDIR +'/tempseg.dat'+subfix
	pcmfile = TEMPDIR +'/temppcm.dat'+subfix
	pcmbytes=''
	while True:
		block = d[npos:npos+CODEC_BLOCK_SIZE]
		if not block:
			break
		npos+=CODEC_BLOCK_SIZE
		f = open(segfile,'wb')
		f.write(block)
		f.close()
		segfile = os.path.normpath(segfile)
		pcmfile = os.path.normpath(pcmfile)

		cmd = u'speex.exe "%s" "%s"'%(segfile,pcmfile)
		r = subprocess.call(cmd.encode('gbk'),shell=True)
		#r = os.system(cmd.encode('gbk'))
		if r :
			print 'speex fail!'
			return ''
		f = open(pcmfile,'rb')
		pcmbytes+=f.read()
		print len(pcmbytes)
		f.close()
	pcmfile = spxfile.replace('.spx','.pcm')
	print 'spx to pcm completed! >> ',pcmfile
	f = open(pcmfile,'wb')
	f.write(pcmbytes)
	f.close()
	print 'preparing pcm to wav ..'
#	wavfile = spxfile.replace('.spx','.wav')
	f = open(wavfile,'wb')
	for n in riffhdr:
		f.write( struct.pack('H',n))
	f.write(pcmbytes)
	f.close()


def wav_to_mp3(spxfile,wavfile,mp3file):
	try:

		spxinfo = format.parseSpxFileInfo(spxfile)
		if not spxinfo:
			getApp().getLogger().info(u'corrupted file %s, be deleted'%(spxinfo))
			#os.remove(spxfile) #删除非法的spx文件
			return False


		if os.path.exists(mp3file):
			os.remove(mp3file)

		wavfile = os.path.normpath(wavfile)
		mp3file = os.path.normpath(mp3file)
		cmd = u'ffmpeg.exe -y -aq 128 -i "%s" "%s"'%(wavfile,mp3file)
		# os.system(cmd.encode('gbk'))
		r = subprocess.call(cmd.encode('gbk'),shell=True)
		if r:
			print 'ffmpeg convert failed!'
			return False
		#添加附属信息
		#  (phone,filename,createtime,duration)  encode json array
		#2013.10.7  spx 头部32字节写入mp3尾部，spx的degist也写入尾部，
		#  mp3-content + magic(4) + spx-degist(32) + spx-hdr(32)
		spx_digest = utils.getfiledigest(spxfile)
		if not spx_digest:
			print 'calc file digest failed!'
			return False

		f = open(spxfile,'rb')
		hdrinfo = f.read(32)
		f.close()

		filename= os.path.basename(spxfile).lower()
		filename = filename.replace('.spx','.mp3')

		# phone = spxinfo.phone    #getApp().getSettings()['phone']
		# createtime = time.mktime(
		# 					(spxinfo.year,
		# 					spxinfo.month,
		# 					spxinfo.day,
		# 					spxinfo.hour,
		# 					spxinfo.minute,
		# 					0,
		# 					0,0,0)) # int(time.time())
		# createtime = int(createtime)

		duration = utils.readImageDuration(mp3file)
		if not duration:
			print 'calc duration failed: 0 size'
			return False

		f = open(mp3file,'ab')
		magic = struct.pack('!I',0xEEAAEEBB)
		f.write(magic)
		f.write(spx_digest)
		f.write(hdrinfo)

		# params=(phone,filename,createtime,duration,spxinfo.index,spxinfo.attr,spxinfo.serial,spx_digest)
#		print params
		# d = json.dumps(params)
		# padding = 'leadtel '+ d + ' '*200
		# padding = padding[:200]
		# f.write(padding)

		f.close()
	except:
		traceback.print_exc()
		return False
	return True

'''
	ffmpeg采用可变码流编码之后，mp3的大小2倍大小与spx格式
	> ffmpeg.exe -aq 128 -i input.spx output.mp3
	奇怪现象：
		8M的 ffmpeg.exe转换的spx文件到MP3大小为700K
		而最新的需要动态库的ffmpeg.exe（未打包一起 ） 的转换spx到mp3大小为530K
		spx的大小 240K
'''

#去除 spx文件自定义的头
def trimTest():
	f = open(r'C:\01.spx','rb')
	d = f.read()
	f.close()
	d = d[:0xa9]
	f = open(r'c:\temp\01.spx','rb')
	c =f.read()
	f.close()
	f = open('c:/00001.spx','wb')
	f.write(d+c)
	f.close()

#切除19字节头部之后还是未能使用  speexdec 进行转换

if __name__ == '__main__':
#	print utils.readImageDuration('c:\\temp\\02.mp3')
	spx_convert_mp3(r'C:\201104101626_000907_xxxxxxxx913386108100.spx','c:/test.wav')
#	print spx_convert_mp3(r'C:\leadtel\record_1072\record\201104101638_000908_xxxxxxxx913917531221.spx','c:/test.wav')
	#trimTest()
