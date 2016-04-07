
python访问 https采用 urllib.urlopen() 
注意： python 的ssl内部采用SSL V2版本 ，apache的 mod_ssl默认是V2版本 ，ssl.conf


语音系统 服务器采用https协议，默认443端口 
https采用单向认证模式，客户端不需要证书就可以访问，
通信链路上的数据传输都将被加密（DES+RSA，DH)，所以数据传输是安全的
webserver登陆时浏览器会提示不信任的CA和证书服务，忽略即可


服务器新版本安装和下载
配置apache添加 /download/ 映射到 /svr/download目录 ， 此目录存放不同终端软件的安装程序 
/svr/audio/setup.cfg配置文件中条目term_version=xxx 指定了最新的软件版本编号

终端软件相关运行、配置文件:
system.lib 数据库文件，如果不存在，终端软件第一次安装将自动将其创建
logdump.yes  如果存在此文件，则将会输出日志内容到当天的日志文件中 
usb.props  记录当前话机最新的语音记录索引，自增，换话机需清除此文件 
system.conf 系统参数配置
