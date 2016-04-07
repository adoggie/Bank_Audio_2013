insert  into audio_organization(name,phone,address,memo) 
values('交行总行',15921556955,'上海市','交行总行哦','1_');
insert  into audio_treenode(name,type,obj_id,level,link) 
values('交行总行',1,1,1,'1_');

insert into audio_user(org_id,"user", passwd,name,phone,address,email,rights)
values(1,'admin','111111','用户1','11111111111','昌里路','1@1.com','1');
insert  into audio_treenode(name,parent_id,type,obj_id,level,link) 
values('用户1',1,2,1,2,'1_2_');