文件的前面32个Bytes是头，剩下的都是数据，每20个Bytes是一个speex数据包；


{
    unsigned short IndexNo;   //序号

    unsigned char  Attribute: 2 ; //来去电属性，0：来电；1：去电 2：录音 3:未接
    unsigned char  DeleteStatus: 1 ;   //这个你不用关心；//1：正常，0：曾经后一条被删除，上电需地址跳跃
    unsigned char  Reserve: 1 ;        //这个你不用关心；//长度补全标记
    unsigned char  Month: 4 ;   //月份

    unsigned short Day: 5 ;     //日期
    unsigned short Hour: 5 ;    //小时
    unsigned short Minute: 6 ;   //分钟

    //移到最后unsigned char  Number[6] ;  //电话号码，每4bit存一个号码，共12号码，Number[0]低4bit为第一个号码，高4bit为第二个号码，类推。0xFF表示为无效号码或表示号码结束。

	unsigned long  FileBeginAddr;   //文件起始位置，删至3个byte，因为原来最后一个byte肯定是0
    
	unsigned long  Filelength;   //文件长度，单位byte，删至2个byte，因为原来最后一个byte肯定是0，最高一个byte删除，这样一个录音文件最长只能4.6小时，chenzhm
    unsigned char  Number[10] ;  //电话号码，每4bit存一个号码，共20号码，Number[0]低4bit为第一个号码，高4bit为第二个号码，类推。0xFF表示为无效号码或表示号码结束。
    unsigned long  LSerialNumber;//电话录音的唯一号。第20个字节开始 
    unsigned char  Year;             //电话记录的年份信息。第24个字节	
}FileInfo; 