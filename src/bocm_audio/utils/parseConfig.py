__author__ = 'daitr'
#--coding:utf-8--
import ConfigParser,os

def getConfigValue(configPath,section,key):
	try:
		if(os.path.exists(configPath)):
			try:
				cf = ConfigParser.ConfigParser()
				cf.read(configPath)
				value = cf.get(section, key)
				return value
			except:
				print u"parse file failure"
				return
		else:
			print u"config file is not exists!"
			return
	except:
		print u"cannot get userinfo from the config.ini"
		return