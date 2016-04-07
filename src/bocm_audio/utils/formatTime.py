__author__ = 'daitr'

def formatTimeLength(secs):
	h = int(secs/3600)
	secs = secs%3600
	m = int(secs/60)
	s = secs%60
	return '%02d:%02d:%02d'%(h,m,s)

if  __name__=="__main__":
	print formatTimeLength(4562)