# -*- coding: utf-8 -*-
import sys,os
import traceback,threading,time,struct,os,os.path,shutil,distutils.dir_util,array,base64,zlib,struct,binascii
import datetime
import json,hashlib,base64


# set DJANGO_SETTINGS_MODULE=bocm_audio.settings
os.putenv("DJANGO_SETTINGS_MODULE","bocm_audio.settings")


from django.http import *
from django.db import transaction


from django.shortcuts import render_to_response



from django.views.decorators.csrf import csrf_exempt


#os.environ["DJANGO_SETTINGS_MODULE"] = "audio.settings"

import audio.models as cm


def usage():
	print 'python clear_archive.py termnial-name'
	
ps = sys.argv[1:]
if not ps:
	print 'param: user not specified!'
	usage()
	sys.exit()

user = ps[0]
term = cm.Terminal.objects.get(user=user)


rs = cm.Archive.objects.filter(term__id=term.id)
print 'total archive number of:%s be eliminated!'%len(rs)
for ar in rs:
	try:
		spxfile = ar.url
		os.remove(spxfile)
	except:
		pass
rs.delete()

rs = cm.Client.objects.filter(term__id = term.id)
rs.delete()
# print term
