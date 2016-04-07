# -*- coding:gb2312 -*-
import sys, traceback,threading,time,os,os.path ,sqlite3

db = sqlite3.connect('system.lib')
db.text_factory = str

def audiofile_resync():
	sql ="update core_audiofile set status=0"
	db.execute(sql)
	db.commit()
	
def audiofile_memo_resync():
	sql ="update core_audiofile set memo_status=0"
	db.execute(sql)
	db.commit()
	
def clientinfo_resync():
	sql = "update core_client set status=0"
	db.execute(sql)
	db.commit()
	

audiofile_resync()
audiofile_memo_resync()
clientinfo_resync()
