# -*- coding:utf-8 -*- 

import os,sys,os.path


sys.path.insert(0,r'E:\Projects\new.tax\src\dz_logistics\tax')

#Calculate the path based on the location of the WSGI script.

os.environ['DJANGO_SETTINGS_MODULE'] = 'tax.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
print application
