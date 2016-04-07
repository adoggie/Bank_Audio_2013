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

@register.tag(name="serial_number")
def do_serial_number(parser, token):
		# split_contents() knows not to split quoted strings.
	bits = token.contents.split()
	realList = [parser.compile_filter(x) for x in bits]
	if len(bits) !=4:
		raise template.TemplateSyntaxError("'serial_number' statement requires three argument")
	else:
#		arg_list = bits[1:4]
#       bits数组中的bits[1],bits[2],bits[3]是模板变量,所以需要parser.compile_filter,这样参数可以不仅仅是已知数值
		arg_list = [parser.compile_filter(x) for x in bits[1:4]]
		return SerialNumberNode(arg_list)


class SerialNumberNode(template.Node):
	'''
	#列表编号的标签
	'''
	def __init__(self, arg_list):
		self.arg_list = arg_list
#		self.numList=[]

	def render(self, context):
		try:
			num_list =[]
			for temp_attr in self.arg_list:
				#解析模板变量
				num_list.append(temp_attr.resolve(context))
			serial_number = (num_list[0]-1)*num_list[1]+num_list[2]
			context['serial_number'] = serial_number
			return serial_number
		except:
			raise template.TemplateSyntaxError("SerialNumber tag error")
