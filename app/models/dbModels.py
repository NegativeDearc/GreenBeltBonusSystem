# -*- coding:utf-8 -*-

from app import db
from werkzeug.security import check_password_hash, generate_password_hash
import datetime


class usrPwd(db.Model):
    '''存储用户名和密码的表'''
    __tablename__ = 'USER_PASSWORD'
    user = db.Column(db.Text(50), nullable=False, unique=True, primary_key=True)
    password = db.Column(db.Text(50), nullable=False)

    def __init__(self, user=None, password=None):
        self.user = user
        self.password = password

    @property
    def pwd(self):
        raise AttributeError('Password is not a readable attribute')

    @pwd.setter
    def pwd(self, pwd):
        self.password = generate_password_hash(pwd, salt_length=16)

    def verify_pwd(self, pwd):
        return check_password_hash(self.password, pwd)


class usrName(db.Model):
    '''存储用户名和密码的表'''
    __tablename__ = 'USER_ID'
    id = db.Column(db.String(50), nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    format_name = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
        self.format_name = '(' + self.id + ')' + self.name


class prjInfo(db.Model):
    '''存储项目信息的表'''
    __tablename__ = 'PRJ_INFO'
    prj_no = db.Column(db.String(50), nullable=False, unique=True, primary_key=True)
    prj_content = db.Column(db.String(128), nullable=False)
    prj_finish_time = db.Column(db.DATE, nullable=False)
    prj_three_month = db.Column(db.DATE, nullable=False)
    prj_six_month = db.Column(db.DATE, nullable=False)
    prj_three_month_check = db.Column(db.BOOLEAN)
    prj_six_month_check = db.Column(db.BOOLEAN)

    def __init__(self, prj_no, prj_content, prj_finish_time, prj_three_month_check=False, prj_six_month_check=False):
        self.prj_no = prj_no
        self.prj_content = prj_content
        try:
            self.prj_finish_time = datetime.datetime.strptime(prj_finish_time, '%m/%d/%Y').date()
        except Exception:
            self.prj_finish_time = datetime.datetime.strptime(prj_finish_time, '%Y/%m/%d').date()
        self.prj_three_month = self.prj_finish_time + datetime.timedelta(days=90)
        self.prj_six_month = self.prj_finish_time + datetime.timedelta(days=180)
        self.prj_six_month_check = prj_six_month_check
        self.prj_three_month_check = prj_three_month_check