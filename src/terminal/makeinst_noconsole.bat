python setup_noconsole.py py2exe -i sip -d release
copy *.txt release
copy *.dll release
copy *.jpg release
copy *.dat release
copy *.conf release
copy *.profile release 
copy *.exe release
copy *.lib release

xcopy resource release\resource /s /e /y

xcopy release\*.* c:\leadtel\bin /e /s /y

pause
