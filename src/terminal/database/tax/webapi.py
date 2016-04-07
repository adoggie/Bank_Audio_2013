# -*- coding: utf-8 -*-
import sys,os
import traceback,threading,time,struct,os,os.path,shutil,distutils.dir_util,array,base64,zlib,struct,binascii
import datetime
import json,hashlib,base64
from django.http import *
from django.db import transaction

from django.shortcuts import render_to_response
import cipher,pickle
from tax.core import models as cm
from dbconn import *

from django.views.decorators.csrf import csrf_exempt




store_path='/home/invoices'
ENCRYPT_KEY='#E0~RweT'
TEST = 0
class ServiceError:
	ERROR_INTERNAL = 999

class WebCallReturn:
	SUCC = 0
	FAILED = 1
	def __init__(self,status = FAILED,
	             ecode= ServiceError.ERROR_INTERNAL ,emsg=''):
		self.status = status
		self.ecode = ecode
		self.emsg = emsg
		self.result ={}
		self.kvs={}

	def assign(self,result):
		self.result = result
		return self

	def httpResponse(self):
		'''
			if jsonp:
				callback_funcName = GET.get('callback')

		'''
		self.kvs['status'] = self.status
		self.kvs['ecode'] = self.ecode
		self.kvs['emsg'] = self.emsg
		if self.result!=None:
			self.kvs['result'] = self.result

		return HttpResponse(json.dumps(self.kvs),mimetype='application/json')

def SuccCallReturn():
	return WebCallReturn(status=WebCallReturn.SUCC,ecode=0)

def FailCallReturn(ecode=ServiceError.ERROR_INTERNAL,emsg=''):
	if not emsg and ecode == ServiceError.ERROR_INTERNAL:
		#emsg = traceback.format_exc()
		print traceback.format_exc()
	return WebCallReturn(ecode=ecode,emsg=emsg)

@transaction.commit_manually
def save(inv):
	try:
		if cm.Invoice.objects.filter(inv_code=inv.inv_code,inv_number=inv.inv_number).count():
			return True
		r = cm.Invoice()
		r.doc_nr = inv.doc_nr
		r.inv_type = inv.inv_type
		r.inv_code = inv.inv_code
		r.inv_number = inv.inv_number
		r.client_nr =inv.client_nr
		r.cust_nr = inv.cust_nr
		r.cust_name = inv.cust_name
		r.cust_tax_code = inv.cust_tax_code
		r.cust_address_tel = inv.cust_address_tel
		r.cust_bank_account = inv.cust_bank_account

		r.inv_date = inv.inv_date
		r.inv_month = inv.inv_month
		r.inv_amount = inv.inv_amount
		r.inv_taxrate = inv.inv_taxrate
		r.inv_tax = inv.inv_tax

		r.taxitem = inv.taxitem
		r.memo = inv.memo
		r.issuer = inv.issuer
		r.checker = inv.checker
		r.payee = inv.payee
		r.flag_dy = inv.flag_dy
		r.flag_zf = inv.flag_zf
		r.flag_qd = inv.flag_qd
		r.flag_xf = inv.flag_xf
		r.flag_dj = inv.flag_dj
		r.flag_wk = inv.flag_wk
		r.seller_name = inv.seller_name
		r.seller_taxcode = inv.seller_taxcode
		r.seller_address = inv.seller_address
		r.seller_bankacct = inv.seller_bankacct
		r.isuploaded = 1
		r.doc_time = inv.doc_time
		r.pay_type = inv.pay_type
		r.save()


		for item in inv.items:
			d = cm.InvoiceItem()
			d.inv_code = inv.inv_code,
			d.inv_number = inv.inv_number
			d.item_nr = item.item_nr
			d.item_name = item.item_name
			d.taxitem = item.taxitem
			d.spec = item.spec
			d.unit = item.unit
			d.qty = item.qty
			d.price = item.price
			d.taxrate = item.taxrate
			d.tax = item.tax
			d.flag_tax = item.flag_tax
			d.discount_amount = item.discount_amount
			d.discount_tax = item.discount_tax
			d.save()
		transaction.commit()
	except:
		transaction.rollback()
		traceback.print_exc()
		return False

	return True


@csrf_exempt
def putInvoice(r):

	try:
		d = r.POST.get('invoices')
		print d
		
		d = base64.decodestring(d)
		d = cipher.decrypt_des(ENCRYPT_KEY,d)
		invoices = pickle.loads(d)
		for inv in invoices:
			if not save(inv):
				return FailCallReturn(msg='code:%s,number:%s'%(inv.inv_code,inv.inv_number))
	except: # timeout or error
		traceback.print_exc()
		return FailCallReturn(msg=traceback.format_exc())
	return SuccCallReturn()

