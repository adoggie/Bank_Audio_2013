�ļ���ǰ��32��Bytes��ͷ��ʣ�µĶ������ݣ�ÿ20��Bytes��һ��speex���ݰ���


{
    unsigned short IndexNo;   //���

    unsigned char  Attribute: 2 ; //��ȥ�����ԣ�0�����磻1��ȥ�� 2��¼�� 3:δ��
    unsigned char  DeleteStatus: 1 ;   //����㲻�ù��ģ�//1��������0��������һ����ɾ�����ϵ����ַ��Ծ
    unsigned char  Reserve: 1 ;        //����㲻�ù��ģ�//���Ȳ�ȫ���
    unsigned char  Month: 4 ;   //�·�

    unsigned short Day: 5 ;     //����
    unsigned short Hour: 5 ;    //Сʱ
    unsigned short Minute: 6 ;   //����

    //�Ƶ����unsigned char  Number[6] ;  //�绰���룬ÿ4bit��һ�����룬��12���룬Number[0]��4bitΪ��һ�����룬��4bitΪ�ڶ������룬���ơ�0xFF��ʾΪ��Ч������ʾ���������

	unsigned long  FileBeginAddr;   //�ļ���ʼλ�ã�ɾ��3��byte����Ϊԭ�����һ��byte�϶���0
    
	unsigned long  Filelength;   //�ļ����ȣ���λbyte��ɾ��2��byte����Ϊԭ�����һ��byte�϶���0�����һ��byteɾ��������һ��¼���ļ��ֻ��4.6Сʱ��chenzhm
    unsigned char  Number[10] ;  //�绰���룬ÿ4bit��һ�����룬��20���룬Number[0]��4bitΪ��һ�����룬��4bitΪ�ڶ������룬���ơ�0xFF��ʾΪ��Ч������ʾ���������
    unsigned long  LSerialNumber;//�绰¼����Ψһ�š���20���ֽڿ�ʼ 
    unsigned char  Year;             //�绰��¼�������Ϣ����24���ֽ�	
}FileInfo; 