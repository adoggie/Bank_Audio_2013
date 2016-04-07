
import os,os.path,sys,string


os.system('python manage.py sqlall core > sql.txt')

f = open('sql.txt')
lines = f.readlines()
f.close()

result=[]
for n in range(len(lines)):
	if lines[n].find('''"id"''') !=-1:
		continue
	result.append(lines[n])

f = open('sql.txt','w')
f.write( string.join(result,''))
f.close()