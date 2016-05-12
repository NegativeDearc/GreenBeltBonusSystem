# -*- coding:utf-8 -*-

from app import db
from sqlalchemy.ext.hybrid import hybrid_method,hybrid_property
from app.ext.rules import ruleMaker
from werkzeug.security import check_password_hash, generate_password_hash
import datetime


class usrPwd(db.Model):
    '''存储用户名和密码的表'''
    __tablename__ = 'USER_PASSWORD'
    user     = db.Column(db.Text(50), nullable=False, unique=True, primary_key=True)
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

    id     = db.Column(db.Integer,nullable=False,unique=True,primary_key=True)
    prj_no = db.Column(db.String(50), nullable=False, unique=True)
    prj_content = db.Column(db.String(128), nullable=False)
    prj_finish_time = db.Column(db.DATE, nullable=False)
    prj_three_month = db.Column(db.DATE, nullable=False)
    prj_six_month   = db.Column(db.DATE, nullable=False)
    prj_three_month_check = db.Column(db.BOOLEAN,default=0)
    prj_six_month_check   = db.Column(db.BOOLEAN,default=0)
    # duplicability + resource_usage + implement_period +
    # kpi_impact + cost_saving = prj_golden_type
    prj_golden_type       = db.Column(db.String(50),nullable=False)
    prj_golden_score      = db.Column(db.Integer,nullable=False)
    #
    prj_level             = db.Column(db.String(50),nullable=False)
    prj_score             = db.Column(db.Integer,nullable=False)
    #
    prj_target_score      = db.Column(db.Integer,nullable=False)
    #
    prj_total_score       = db.Column(db.Integer,nullable=False)
    prj_active_score      = db.Column(db.Numeric(128),default=0)
    #
    def __init__(self,form):
        rul = ruleMaker()

        self.prj_no = form.get('prj_name')
        self.prj_content = form.get('prj_des')
        #
        try:
            self.prj_finish_time = datetime.datetime.strptime(form.get('prj_date'), '%m/%d/%Y').date()
        except Exception:
            self.prj_finish_time = datetime.datetime.strptime(form.get('prj_date'), '%Y/%m/%d').date()
        #
        self.prj_three_month = self.prj_finish_time + datetime.timedelta(days=90)
        self.prj_six_month = self.prj_finish_time + datetime.timedelta(days=180)
        #
        self.prj_cost_saving  = form.get('cost_saving')
        self.prj_golden_type  = rul.golden_type_judging(form.get('score_sum'))

        self.prj_golden_score = int(rul.rules_api_info()[self.prj_golden_type]['value'])
        self.prj_target_score = int(form.get('target_score'))
        #
        if form.has_key('type_s'):
            self.prj_level = 'S'
            self.prj_score = int(rul.rules_api_info()['s']['value'])
            # S类型无须检查
            self.prj_three_month_check = True
            self.prj_six_month_check = True
            self.prj_total_score = self.prj_score + self.prj_golden_score + self.prj_target_score
            # S类型直接激活分值
            self.prj_active_score = self.prj_total_score
        if form.has_key('type_p'):
            self.prj_level = 'P'
            self.prj_score = int(rul.rules_api_info()['p']['value'])
            self.prj_total_score = self.prj_score + self.prj_golden_score + self.prj_target_score
        if form.has_key('type_k'):
            self.prj_level = 'K'
            self.prj_score = int(rul.rules_api_info()['k']['value'])
            self.prj_total_score = self.prj_score + self.prj_golden_score + self.prj_target_score
        if form.has_key('type_g'):
            self.prj_level = 'G'
            self.prj_score = int(rul.rules_api_info()['g']['value'])
            self.prj_total_score = self.prj_score + self.prj_golden_score + self.prj_target_score
        if form.has_key('type_b'):
            self.prj_level = 'B'
            self.prj_score = int(rul.rules_api_info()['b']['value'])
            self.prj_total_score = self.prj_score + self.prj_golden_score + self.prj_target_score

    # 可针对实例或者类使用该方法
    @hybrid_property
    def data_3_month(self):
        now = datetime.datetime.now().date()
        now_before_2_days = now + datetime.timedelta(days=2)
        now_after_30_days = now - datetime.timedelta(days=30)
        if self.prj_three_month_check is not True:
            if self.prj_three_month < now_before_2_days and \
                            self.prj_three_month > now_after_30_days:
                return self.prj_no
            else:
                return -1
        else:
            return -2

class prjMem(db.Model):
    '''储存项目用户清单的表'''
    __tablename__ = 'PRJ_MEM'

    id           = db.Column(db.Integer,nullable=False,primary_key=True)
    prj_no       = db.Column(db.String(50),nullable=True)
    mem_name     = db.Column(db.String(50),nullable=False)
    mem_role     = db.Column(db.String(50),nullable=False)
    mem_mono     = db.Column(db.String(50),default=None)
    score_ratio  = db.Column(db.Float(50))
    score_or_not = db.Column(db.BOOLEAN,default=True)
    # 定义双向关系

    def __init__(self,*args):
        '''app.ext.function register_mem_info'''
        self.prj_no       = args[0]
        self.mem_name     = args[1]
        self.mem_role     = args[2]

        if args[3] == 0:
            self.score_or_not = False
        else:
            self.score_or_not = True

        self.mem_mono     = args[4]
        self.score_ratio  = args[5]