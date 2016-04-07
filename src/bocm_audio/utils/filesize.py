__author__ = 'daitr'

def intB2ReadableStr(size):
	size *= 1.0
	if size < 0:
		raise Exception("filesize should  be positive number! ")
	if size <1024:
		return "%.2f B" % size
	elif size <1024*1024:
		return "%.2f KB" % (size/1024)
	elif size <1024*024*1024:
		return "%.2f MB" % (size/(1024*1024))
	else:
		return "%.2f GB" % (size/(1024*1024*1024))
if  __name__=="__main__":

	print intB2ReadableStr(1023)
	print intB2ReadableStr(1024)
	print intB2ReadableStr(1025)
	print intB2ReadableStr(1024*1024-1)
	print intB2ReadableStr(1024*1024)
	print intB2ReadableStr(1024*1024+1)
	print intB2ReadableStr(1024*1024*1024-1)
	print intB2ReadableStr(1024*1024*1024)
	print intB2ReadableStr(1024*1024*1024+1)
	print intB2ReadableStr(1024*1024*1024*1024-1)
	print intB2ReadableStr(1024*1024*1024*1024)
	print intB2ReadableStr(1024*1024*1024*1024+1)
	print intB2ReadableStr(1024*1024*1024*1024*1024-1)
	print intB2ReadableStr(1024*1024*1024*1024*1024)
	print intB2ReadableStr(1024*1024*1024*1024*1024+1)