BEGIN;
CREATE TABLE "audio_organization" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(80) NOT NULL,
    "parent_id" integer,
    "phone" varchar(20),
    "address" varchar(200),
    "memo" text,
    "link" varchar(320) NOT NULL
)
;
ALTER TABLE "audio_organization" ADD CONSTRAINT "parent_id_refs_id_3933cc37" FOREIGN KEY ("parent_id") REFERENCES "audio_organization" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE "audio_user" (
    "id" serial NOT NULL PRIMARY KEY,
    "org_id" integer NOT NULL REFERENCES "audio_organization" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user" varchar(40) NOT NULL,
    "passwd" varchar(20) NOT NULL,
    "name" varchar(40),
    "phone" varchar(30),
    "address" varchar(120),
    "email" varchar(40),
    "rights" integer NOT NULL
)
;
CREATE TABLE "audio_terminal" (
    "id" serial NOT NULL PRIMARY KEY,
    "org_id" integer NOT NULL REFERENCES "audio_organization" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user" varchar(40) NOT NULL,
    "passwd" varchar(20) NOT NULL,
    "address" varchar(160),
    "phone" varchar(30),
    "postcode" varchar(20),
    "employee" varchar(20),
    "addition" text,
    "creator_id" integer NOT NULL REFERENCES "audio_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "createtime" timestamp with time zone NOT NULL,
    "status" integer NOT NULL,
    "regtime" timestamp with time zone
)
;
CREATE TABLE "audio_archive" (
    "id" serial NOT NULL PRIMARY KEY,
    "term_id" integer NOT NULL REFERENCES "audio_terminal" ("id") DEFERRABLE INITIALLY DEFERRED,
    "digest" varchar(40) NOT NULL,
    "spx_digest" varchar(40) NOT NULL,
    "phone" varchar(40) NOT NULL,
    "name" varchar(80) NOT NULL,
    "path" varchar(200) NOT NULL,
    "size" integer NOT NULL,
    "rectime" timestamp with time zone NOT NULL,
    "duration" integer NOT NULL,
    "uptime" timestamp with time zone NOT NULL,
    "index" integer NOT NULL,
    "attr" integer NOT NULL,
    "serial" integer NOT NULL,
    "memo" text,
    "client_id" integer,
    "type" integer NOT NULL,
    "productid" varchar(40)
)
;
CREATE TABLE "audio_treenode" (
    "id" serial NOT NULL PRIMARY KEY,
    "parent_id" integer,
    "name" varchar(80) NOT NULL,
    "type" integer NOT NULL,
    "obj_id" integer NOT NULL,
    "level" integer NOT NULL,
    "link" varchar(320) NOT NULL
)
;
ALTER TABLE "audio_treenode" ADD CONSTRAINT "parent_id_refs_id_64ee133d" FOREIGN KEY ("parent_id") REFERENCES "audio_treenode" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE "audio_syssettings" (
    "id" serial NOT NULL PRIMARY KEY,
    "key" varchar(80) NOT NULL,
    "value" text,
    "memo" text
)
;
CREATE TABLE "audio_client" (
    "id" serial NOT NULL PRIMARY KEY,
    "term_id" integer NOT NULL REFERENCES "audio_terminal" ("id") DEFERRABLE INITIALLY DEFERRED,
    "sid" varchar(40) NOT NULL,
    "name" varchar(40) NOT NULL,
    "sex" integer NOT NULL,
    "corp" varchar(40),
    "phone1" varchar(30),
    "phone2" varchar(30),
    "address" varchar(100),
    "postcode" varchar(20),
    "email" varchar(40),
    "website" varchar(40),
    "im" varchar(60),
    "memo" text,
    "personid" varchar(40),
    "clientid" varchar(40)
)
;
ALTER TABLE "audio_archive" ADD CONSTRAINT "client_id_refs_id_7f85a337" FOREIGN KEY ("client_id") REFERENCES "audio_client" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "audio_organization_parent_id" ON "audio_organization" ("parent_id");
CREATE INDEX "audio_user_org_id" ON "audio_user" ("org_id");
CREATE INDEX "audio_user_user" ON "audio_user" ("user");
CREATE INDEX "audio_user_user_like" ON "audio_user" ("user" varchar_pattern_ops);
CREATE INDEX "audio_user_passwd" ON "audio_user" ("passwd");
CREATE INDEX "audio_user_passwd_like" ON "audio_user" ("passwd" varchar_pattern_ops);
CREATE INDEX "audio_user_name" ON "audio_user" ("name");
CREATE INDEX "audio_user_name_like" ON "audio_user" ("name" varchar_pattern_ops);
CREATE INDEX "audio_terminal_org_id" ON "audio_terminal" ("org_id");
CREATE INDEX "audio_terminal_user" ON "audio_terminal" ("user");
CREATE INDEX "audio_terminal_user_like" ON "audio_terminal" ("user" varchar_pattern_ops);
CREATE INDEX "audio_terminal_passwd" ON "audio_terminal" ("passwd");
CREATE INDEX "audio_terminal_passwd_like" ON "audio_terminal" ("passwd" varchar_pattern_ops);
CREATE INDEX "audio_terminal_phone" ON "audio_terminal" ("phone");
CREATE INDEX "audio_terminal_phone_like" ON "audio_terminal" ("phone" varchar_pattern_ops);
CREATE INDEX "audio_terminal_employee" ON "audio_terminal" ("employee");
CREATE INDEX "audio_terminal_employee_like" ON "audio_terminal" ("employee" varchar_pattern_ops);
CREATE INDEX "audio_terminal_creator_id" ON "audio_terminal" ("creator_id");
CREATE INDEX "audio_terminal_createtime" ON "audio_terminal" ("createtime");
CREATE INDEX "audio_archive_term_id" ON "audio_archive" ("term_id");
CREATE INDEX "audio_archive_digest" ON "audio_archive" ("digest");
CREATE INDEX "audio_archive_digest_like" ON "audio_archive" ("digest" varchar_pattern_ops);
CREATE INDEX "audio_archive_spx_digest" ON "audio_archive" ("spx_digest");
CREATE INDEX "audio_archive_spx_digest_like" ON "audio_archive" ("spx_digest" varchar_pattern_ops);
CREATE INDEX "audio_archive_phone" ON "audio_archive" ("phone");
CREATE INDEX "audio_archive_phone_like" ON "audio_archive" ("phone" varchar_pattern_ops);
CREATE INDEX "audio_archive_name" ON "audio_archive" ("name");
CREATE INDEX "audio_archive_name_like" ON "audio_archive" ("name" varchar_pattern_ops);
CREATE INDEX "audio_archive_path" ON "audio_archive" ("path");
CREATE INDEX "audio_archive_path_like" ON "audio_archive" ("path" varchar_pattern_ops);
CREATE INDEX "audio_archive_memo" ON "audio_archive" ("memo");
CREATE INDEX "audio_archive_memo_like" ON "audio_archive" ("memo" text_pattern_ops);
CREATE INDEX "audio_archive_client_id" ON "audio_archive" ("client_id");
CREATE INDEX "audio_archive_type" ON "audio_archive" ("type");
CREATE INDEX "audio_archive_productid" ON "audio_archive" ("productid");
CREATE INDEX "audio_archive_productid_like" ON "audio_archive" ("productid" varchar_pattern_ops);
CREATE INDEX "audio_treenode_parent_id" ON "audio_treenode" ("parent_id");
CREATE INDEX "audio_syssettings_key" ON "audio_syssettings" ("key");
CREATE INDEX "audio_syssettings_key_like" ON "audio_syssettings" ("key" varchar_pattern_ops);
CREATE INDEX "audio_client_term_id" ON "audio_client" ("term_id");
CREATE INDEX "audio_client_sid" ON "audio_client" ("sid");
CREATE INDEX "audio_client_sid_like" ON "audio_client" ("sid" varchar_pattern_ops);
CREATE INDEX "audio_client_name" ON "audio_client" ("name");
CREATE INDEX "audio_client_name_like" ON "audio_client" ("name" varchar_pattern_ops);
CREATE INDEX "audio_client_phone1" ON "audio_client" ("phone1");
CREATE INDEX "audio_client_phone1_like" ON "audio_client" ("phone1" varchar_pattern_ops);
CREATE INDEX "audio_client_phone2" ON "audio_client" ("phone2");
CREATE INDEX "audio_client_phone2_like" ON "audio_client" ("phone2" varchar_pattern_ops);
CREATE INDEX "audio_client_address" ON "audio_client" ("address");
CREATE INDEX "audio_client_address_like" ON "audio_client" ("address" varchar_pattern_ops);
CREATE INDEX "audio_client_email" ON "audio_client" ("email");
CREATE INDEX "audio_client_email_like" ON "audio_client" ("email" varchar_pattern_ops);
CREATE INDEX "audio_client_website" ON "audio_client" ("website");
CREATE INDEX "audio_client_website_like" ON "audio_client" ("website" varchar_pattern_ops);
CREATE INDEX "audio_client_im" ON "audio_client" ("im");
CREATE INDEX "audio_client_im_like" ON "audio_client" ("im" varchar_pattern_ops);
CREATE INDEX "audio_client_memo" ON "audio_client" ("memo");
CREATE INDEX "audio_client_memo_like" ON "audio_client" ("memo" text_pattern_ops);
CREATE INDEX "audio_client_personid" ON "audio_client" ("personid");
CREATE INDEX "audio_client_personid_like" ON "audio_client" ("personid" varchar_pattern_ops);
CREATE INDEX "audio_client_clientid" ON "audio_client" ("clientid");
CREATE INDEX "audio_client_clientid_like" ON "audio_client" ("clientid" varchar_pattern_ops);
COMMIT;
