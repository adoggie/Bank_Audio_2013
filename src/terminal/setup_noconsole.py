# -*- coding:utf-8 -*-
from distutils.core import setup
import py2exe


setup(windows=[{"script":"main.py", "icon_resources":[(1, "leadcom.ico")]
          }]
)


#setup(console=[{"script":"main.py",
#          "icon_resources":[(1, "app_tax.ico")]}]
#)


#setup(name='Game EndPointService',
#			version='1.0',
#			description='Game Distribution Por',
#			author='scott',
#			author_email='zhangbin@5173.com',
#			url='',
#			#packages=['distutils', 'distutils.command'],
#			py_modules=['endpoint']
#			
#			)
