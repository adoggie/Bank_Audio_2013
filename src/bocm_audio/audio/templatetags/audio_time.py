#-*-coding:UTF-8-*-
'''
Created on 2012-3-11

@author: DTR
'''
import datetime
import os

from django.utils.safestring import mark_safe
from django import template


register = template.Library()


def duration_format(secs):
	h = int(secs/3600)
	secs = secs%3600
	m = int(secs/60)
	s = secs%60
	return '%02d:%02d:%02d'%(h,m,s)
duration_format.is_safe = True
register.filter(duration_format)