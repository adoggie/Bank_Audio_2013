insert  into audio_organization(name,phone,address,memo) 
values('交行总行',15921556955,'上海市','交行总行哦');
insert  into audio_treenode(name,type,obj_id,level,link) 
values('交行总行',1,1,1,'1_');

insert into audio_user(org_id,"user", passwd,name,phone,address,email,rights)
values(1,'user1','111111','用户1','11111111111','昌里路','1@1.com','1');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('用户1',1,2,1,2,'1_2_');

insert  into audio_terminal(org_id,"user",passwd,address,phone,postcode,employee,addition,creator_id,createtime,status,regtime) 
values(1,'terminaluser','111111','浦东昌里','021-1111111','200000','小张','附属信息',1,'2013-01-01 00:00:00',0,'2013-01-01 00:00:00');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('terminaluser',1,3,1,2,'1_3_');


insert  into audio_organization(name,parent_id,phone,address,memo) 
values('上海分行',1,15921556955,'上海市','交行总行哦');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('上海分行',1,1,2,2,'1_4_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行1',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行1',4,1,7,3,'1_4_9_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行2',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行2',4,1,8,3,'1_4_10_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行3',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行3',4,1,9,3,'1_4_11_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行4',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行4',4,1,10,3,'1_4_12_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行5',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行5',4,1,11,3,'1_4_13_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行6',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行6',4,1,12,3,'1_4_14_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行7',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行7',4,1,13,3,'1_4_15_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行8',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行8',4,1,14,3,'1_4_16_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行9',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行9',4,1,15,3,'1_4_17_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行10',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行10',4,1,16,3,'1_4_18_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行11',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行11',4,1,17,3,'1_4_19_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行12',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行12',4,1,18,3,'1_4_20_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行13',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行13',4,1,19,3,'1_4_21_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行14',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行14',4,1,20,3,'1_4_22_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行15',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行15',4,1,21,3,'1_4_23_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行16',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行16',4,1,22,3,'1_4_24_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行17',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行17',4,1,23,3,'1_4_25_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行18',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行18',4,1,24,3,'1_4_26_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行19',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行19',4,1,25,3,'1_4_27_');

insert  into audio_organization(name,parent_id,phone,address,memo) 
values('浦东支行20',2,15921556955,'上海市','浦东支行');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('浦东支行20',4,1,26,3,'1_4_28_');

select * from audio_archive;
insert into audio_archive(term_id,digest,spx_digest,phone,name,path,size,rectime,duration,uptime,index,attr,serial,memo,client_id,type,productid)
values(1,'digest','spx_digest','1111111','luyin1','/aa/',1024,'2013-01-01',120,'2013-01-01',1,1,11111,'luyinooo',1,1,'productid')

