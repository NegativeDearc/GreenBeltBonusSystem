# -*- coding:utf-8 -*-

from app import db
from werkzeug.security import check_password_hash,generate_password_hash

class usrPwd(db.Model):
    '''存储用户名和密码的表'''
    __tablename__ = 'USER_PASSWORD'
    user     = db.Column(db.Text(50),nullable=False,unique=True,primary_key=True)
    password = db.Column(db.Text(50),nullable=False)

    @property
    def pwd(self):
        raise AttributeError('Password is not a readable attribute')

    @pwd.setter
    def pwd(self,pwd):
        self.password = generate_password_hash(pwd,salt_length=16)

    def verify_pwd(self,pwd):
        return check_password_hash(self.password,pwd)

class usrName(db.Model):
    '''存储用户名和密码的表'''
    __tablename__ = 'USER_ID'
    id          = db.Column(db.String(50),nullable=False,unique=True,primary_key=True)
    name        = db.Column(db.String(50),nullable=False,unique=True)
    format_name = db.Column(db.String(50),nullable=False,unique=True)

    def name_formatter(self):
        self.format_name = '(' + self.id + ')' + self.name