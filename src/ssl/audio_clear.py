#! /usr/bin/python

import os,os.path,time

distance = 3600*24  # one day

def cleanup():
	store_dir = '/svr/temp'
	files = os.listdir(store_dir)
	for f in files:
		mt = os.path.getmtime(os.path.join(store_dir,f))
		if time.time() - mt > distance:
			print 'delete file:',f
	
if __name__=='__main__':
	cleanup()
