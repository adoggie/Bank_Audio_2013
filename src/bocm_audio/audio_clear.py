#! /usr/bin/python

import os,os.path,time

distance = 3600*24  # one day

def cleanup():
	store_dir = '/svr/temp'
	files = os.listdir(store_dir)
	for f in files:
		file = os.path.join(store_dir,f)
		mt = os.path.getmtime(file)
		if time.time() - mt > distance:
			print 'delete file:',file
			os.remove(file)
	
if __name__=='__main__':
	cleanup()
