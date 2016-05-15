# -*- coding:utf-8 -*-

from app import db
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from app.ext.rules import ruleMaker
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

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    prj_no = db.Column(db.String(50), nullable=False, unique=True)
    prj_content = db.Column(db.String(128), nullable=False)
    prj_finish_time = db.Column(db.DATE, nullable=False)
    prj_three_month = db.Column(db.DATE, nullable=False)
    prj_six_month = db.Column(db.DATE, nullable=False)
    prj_three_month_check = db.Column(db.BOOLEAN, default=0)
    prj_six_month_check = db.Column(db.BOOLEAN, default=0)
    # duplicability + resource_usage + implement_period +
    # kpi_impact + cost_saving = prj_golden_type
    prj_golden_type = db.Column(db.String(50), nullable=False)
    prj_golden_score = db.Column(db.Integer, nullable=False)
    #
    prj_level = db.Column(db.String(50), nullable=False)
    prj_score = db.Column(db.Integer, nullable=False)
    #
    prj_target_score = db.Column(db.Integer, nullable=False)
    #
    prj_total_score = db.Column(db.Numeric(128), nullable=False)
    prj_active_score = db.Column(db.Numeric(128), default=0)

    #
    # member = db.relationship('prjMem',backref = 'prjInfo')
    #
    def __init__(self, form):
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
        self.prj_cost_saving = form.get('cost_saving')
        self.prj_golden_type = rul.golden_type_judging(form.get('score_sum'))
        #
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

    # 可针对单个实例或者类使用该方法
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
            return -1

    # 以下动作请小心，释放分值和关闭针对符合条件的项目
    # 若在query all 之后使用该property 会使数据库全部数据都释放/关闭
    # 操作完毕请提交session
    @hybrid_property
    def data_6_month(self):
        now = datetime.datetime.now().date()
        now_before_2_days = now + datetime.timedelta(days=2)
        now_after_30_days = now - datetime.timedelta(days=30)
        if self.prj_six_month_check is not True:
            if self.prj_six_month < now_before_2_days and \
                            self.prj_six_month > now_after_30_days:
                return self.prj_no
            else:
                return -1
        else:
            return -1

    @hybrid_property
    def pass_3_month(self):
        r = ruleMaker().rules_api_info()
        self.prj_active_score = float(r['check_3']) * float(self.prj_total_score) \
                                + float(self.prj_active_score)
        self.prj_three_month_check = True
        return 1

    @hybrid_property
    def close_3_month(self):
        self.prj_three_month_check = True
        self.prj_six_month_check = True
        return 1

    @hybrid_property
    def pass_6_month(self):
        r = ruleMaker().rules_api_info()
        self.prj_active_score = float(r['check_6']) * float(self.prj_total_score) \
                                + float(self.prj_active_score)
        self.prj_six_month_check = True
        return 1

    @hybrid_property
    def close_6_month(self):
        self.prj_six_month_check = True
        return 1


class prjMem(db.Model):
    '''储存项目用户清单的表'''
    __tablename__ = 'PRJ_MEM'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    prj_no = db.Column(db.String(50), nullable=True)
    mem_name = db.Column(db.String(50), nullable=False)
    mem_role = db.Column(db.String(50), nullable=False)
    mem_mono = db.Column(db.String(50), default=None)
    score_ratio = db.Column(db.Float(50))
    score_or_not = db.Column(db.BOOLEAN, default=True)

    #
    # prjinfo_id   = db.Column(db.Integer,db.ForeignKey('PRJ_INFO.id'))
    # 定义双向关系

    def __init__(self, *args, **kwargs):
        '''app.ext.function register_mem_info'''
        self.prj_no = args[0]
        self.mem_name = args[1]
        self.mem_role = args[2]

        if args[3] == 0:
            self.score_or_not = False
        else:
            self.score_or_not = True

        if self.mem_role in ['C', 'D']:
            self.score_ratio = float(args[5]) / float(kwargs[self.mem_role])
        else:
            self.score_ratio = args[5]
        self.mem_mono = args[4]


class prjRecord(db.Model):
    '''储存用户分值发放的表'''
    __tablename__ = 'PRJ_REC'
    # __mapper_args__ = {'column_prefix':'rec_'}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    prj_no = db.Column(db.String(50))
    prj_mem = db.Column(db.String(50))
    prj_role = db.Column(db.String(50))
    mem_mono = db.Column(db.String(50))
    role_ratio = db.Column(db.Float(50))
    score_or_not = db.Column(db.BOOLEAN)
    #
    score = db.Column(db.Numeric(128))
    prj_action = db.Column(db.String(128))
    action_date = db.Column(db.Date)

    def __init__(self, prj_no, prj_mem, prj_role, mem_mono, role_ratio, score_or_not, score, prj_action, action_date):
        self.prj_no = prj_no
        self.prj_mem = prj_mem
        self.prj_role = prj_role
        self.mem_mono = mem_mono
        self.role_ratio = role_ratio
        self.score_or_not = score_or_not
        self.score = score
        self.prj_action = prj_action
        self.action_date = action_date


class ScoreRelease(object):
    '''日志数据库的动作'''

    def __init__(self, prj_no):
        from app.ext.rules import ruleMaker

        self.rul = ruleMaker().rules_api_info()
        self.q1  = db.session.query(prjInfo.prj_total_score).filter(prjInfo.prj_no == prj_no).first()

        self.q2  = db.session.query(prjMem.prj_no,
                                    prjMem.mem_name,
                                    prjMem.mem_role,
                                    prjMem.mem_mono,
                                    prjMem.score_ratio,
                                    prjMem.score_or_not).filter(prjMem.prj_no == prj_no).all()

        self.now = datetime.datetime.now().date()

    def prj_launch(self, form):
        if form.has_key('type_s'):
            for x in self.q2:
                db.session.add(prjRecord(
                    x.prj_no,
                    x.mem_name,
                    x.mem_role,
                    x.mem_mono,
                    x.score_ratio,
                    x.score_or_not,
                    x.score_ratio * float(self.q1.prj_total_score),
                    u'项目上线成功,S类直接释放分值',
                    self.now
                ))
        else:
            for x in self.q2:
                db.session.add(prjRecord(
                    x.prj_no,
                    x.mem_name,
                    x.mem_role,
                    x.mem_mono,
                    x.score_ratio,
                    x.score_or_not,
                    x.score_ratio * 0.0,
                    u'项目上线成功,但未达到释放分值条件',
                    self.now
                ))
        db.session.commit()
        return 1

    def prj_3_release(self):
        for x in self.q2:
            db.session.add(prjRecord(
                x.prj_no,
                x.mem_name,
                x.mem_role,
                x.mem_mono,
                x.score_ratio,
                x.score_or_not,
                x.score_ratio * float(self.q1.prj_total_score) * float(self.rul['check_3']),
                u'项目通过三个月检查点,释放比例为%s'  % self.rul['check_3'],
                self.now
            ))
        db.session.commit()
        return 1

    def prj_3_close(self):
        for x in self.q2:
            db.session.add(prjRecord(
                x.prj_no,
                x.mem_name,
                x.mem_role,
                x.mem_mono,
                x.score_ratio,
                x.score_or_not,
                x.score_ratio * 0,
                u'项目未通过三个月检查点,不得分',
                self.now
            ))
        db.session.commit()
        return 1

    def prj_6_release(self):
        for x in self.q2:
            db.session.add(prjRecord(
                x.prj_no,
                x.mem_name,
                x.mem_role,
                x.mem_mono,
                x.score_ratio,
                x.score_or_not,
                x.score_ratio * float(self.q1.prj_total_score) * float(self.rul['check_6']),
                u'项目通过六个月检查点,释放比例为%s'  % self.rul['check_6'],
                self.now
            ))
        db.session.commit()
        return 1

    def prj_6_close(self):
        for x in self.q2:
            db.session.add(prjRecord(
                x.prj_no,
                x.mem_name,
                x.mem_role,
                x.mem_mono,
                x.score_ratio,
                x.score_or_not,
                x.score_ratio * 0,
                u'项目未通过六个月检查点,不得分',
                self.now
            ))
        db.session.commit()
        return 1


class SearchDetail(object):
    '''searh页面的积分明细'''
    def __init__(self,form):
        self.name = form.get('employee_name')
        self.rul = ruleMaker().rules_api_info()

    def score_detail(self):

        d = db.session.query(prjInfo,prjMem).\
            outerjoin(prjMem,prjInfo.prj_no == prjMem.prj_no).\
            filter(prjMem.mem_name == self.name).\
            group_by(prjInfo.prj_no).\
            all()

        x = []


        # total_personal_score----------->|项目分数总和
        # total_frozen_score------------->|无效分总和
        # total_active_score------------->|激活分总和
        # total_waiting_to_active_score-->|等待积分激活的总和
        total_personal_score          = 0
        total_frozen_score            = 0
        total_active_score            = 0
        total_waiting_to_active_score = 0

        for e in d:
            # personal_total_score----------->|个人能获得的总分值
            # frozen_score:------------------>|无效分值
            # active_score:------------------>|已经激活的分值
            # waiting_to_active_score:------->|等待激活的分值
            # a:----------------------------->|项目起始发放的分值,目前为S类
            # b:----------------------------->|3个月发放的分值
            # c:----------------------------->|6个月发放的分值
            #

            personal_total_score = float(e.prjInfo.prj_total_score) * float(e.prjMem.score_ratio)

            if e.prjMem.score_or_not:
                frozen_score = personal_total_score
                active_score = 0
                waiting_to_active_score = 0
                a = 0
                b = 0
                c = 0
            else:
                frozen_score = 0
                active_score = float(e.prjInfo.prj_active_score) * float(e.prjMem.score_ratio)

                if e.prjInfo.prj_level == u'S':
                    waiting_to_active_score = 0
                    a = personal_total_score
                    b = 0
                    c = 0
                else:
                    waiting_to_active_score = personal_total_score - active_score
                    a = 0
                    b = personal_total_score * float(self.rul['check_3'])
                    c = personal_total_score * float(self.rul['check_6'])

            x.append([e.prjInfo.prj_no,
                      e.prjMem.mem_role,
                      e.prjInfo.prj_finish_time,
                      e.prjInfo.prj_level,
                      float(e.prjInfo.prj_total_score),
                      float(e.prjInfo.prj_total_score) * float(e.prjMem.score_ratio),
                      e.prjMem.score_or_not,
                      active_score,
                      waiting_to_active_score,
                      frozen_score,
                      a,
                      b,
                      c
                      ])

            # 积分汇总
            total_personal_score          += personal_total_score
            total_frozen_score            += frozen_score
            total_active_score            += active_score
            total_waiting_to_active_score += waiting_to_active_score

        y = {'a':total_personal_score,
             'b':total_active_score,
             'c':total_waiting_to_active_score,
             'd':total_frozen_score}
        return x,y