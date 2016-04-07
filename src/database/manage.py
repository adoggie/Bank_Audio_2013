#!/usr/bin/env python
import os
import sys


sys.path.insert(0,r'C:\projects\leadtel\src')
sys.path.insert(0,r'F:\projects\leadtel_audio\trunk\src')

#sys.path.insert(0,r'C:\projects\leadtel_audio\src')
#sys.path.insert(0,r'C:\projects\leadtel_audio\src\database')

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "audio.settings")
	from django.core.management import execute_from_command_line
	execute_from_command_line(sys.argv)
