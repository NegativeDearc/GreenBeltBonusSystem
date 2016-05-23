# -*- coding:utf-8 -*-
__author__ = 'SXChen'

import datetime

from app import db
from app.models.dbModels import prjRecord
from sqlalchemy import distinct, func
from itertools import chain
from prettytable import PrettyTable
from collections import OrderedDict
from calendar import monthrange

class ReportDetail(object):
    '''
    /report的后台处理模块
    流程: 接受一个日期范围 ->
         在日期范围提取用户名列表集合 ->
         按人员名单遍历明细 ->
         明细折叠输出      ->
         jsPDF打印成pdf
    '''

    def __init__(self, begin, end):
        '''
        处理来自jquery datepicker的日期格式,
        datepicker可在option中采用多种各种.
        '''

        # 为了避免提交时传入空值或无法处理的值导致的出错
        # 这里采用默认的月初和月首作为数据库的传入
        try:
            self.date_begin = datetime.datetime.strptime(begin, '%m/%d/%Y').date()
        except ValueError:
            self.date_begin = datetime.date.today().replace(day=1)

        try:
            self.date_end = datetime.datetime.strptime(end, '%m/%d/%Y').date()
        except ValueError:
            today = datetime.date.today()
            _, last_day = monthrange(today.year,today.month)
            self.date_end = datetime.date(today.year,today.month,last_day)

    def name_set(self):
        '''
        a = [(u'(060090)Zhang Meng',), (u'(134793)Leon Wang',)]
        |||
        map(lambda x:list(x),names)
        |||
        b = [[u'(060090)Zhang Meng'], [u'(134793)Leon Wang']]
        |||
        list(chain(*map(lambda x:list(x),names)))
        |||
        c = [u'(060090)Zhang Meng', u'(134793)Leon Wang']

        '''

        # 因为在后面采用的是以名字为key的集合存储,在这里使用order_by没有意义
        # 后采用OrderedDict()解决问题
        names = db.session.query(distinct(prjRecord.prj_mem)).\
            filter(prjRecord.action_date >= self.date_begin,
                   prjRecord.action_date <= self.date_end).\
            order_by(prjRecord.prj_mem). \
            all()

        name_list = list(chain(*map(lambda x: list(x), names)))

        return name_list

    def record_detail(self):
        '''
        生成成员的项目细则
        即便成员不得分,也应该显示具体信息
        +--------------------+-------------+------------+--------------+--------------+---------------+-----------------+
        |       Member       | Action Date | Project id | Role Defined | Score Ration | Frozen Score? |      Score      |
        +--------------------+-------------+------------+--------------+--------------+---------------+-----------------+
        | (060065)Fu Jiaying |  2016-05-14 | 815u9015j  |      A       |     0.2      |     False     | 1032.4000000000 |
        +--------------------+-------------+------------+--------------+--------------+---------------+-----------------+
        '''
        detail_set = OrderedDict()
        names = ReportDetail.name_set(self)

        def format_tb(raw):
            '''格式化为pretty table'''

            # 表头tb.field_names 必须和 e 中选取元素长度相同
            tb = PrettyTable()
            tb.field_names = ['Member', 'Action Date', 'Project id', 'Role Defined',
                              'Score Ration', 'Invalid Score?', 'Score']
            for e in raw:
                tb.add_row([
                    e.prj_mem,
                    e.action_date,
                    e.prj_no,
                    e.prj_role,
                    e.role_ratio,
                    e.score_or_not,
                    e.score
                ])
            return tb

        for name in names:
            r = db.session.query(prjRecord.prj_mem,
                                 prjRecord.action_date,
                                 prjRecord.prj_no,
                                 prjRecord.prj_role,
                                 prjRecord.role_ratio,
                                 prjRecord.score_or_not,
                                 prjRecord.score). \
                filter(prjRecord.prj_mem == name). \
                order_by(prjRecord.prj_no). \
                all()
            detail_set.update({name: format_tb(r)})
        return detail_set

    def score_detail(self):
        '''
        得分的细则,
        按类分别
        '''
        score_set = OrderedDict()
        names = ReportDetail.name_set(self)
        for name in names:
            # 按照角色分类进行聚合
            r1 = db.session.query(func.sum(prjRecord.score).label('Sum')). \
                filter(prjRecord.score_or_not == False,
                       prjRecord.prj_role == 'A',
                       prjRecord.prj_mem == name). \
                all()
            r2 = db.session.query(func.sum(prjRecord.score).label('Sum')). \
                filter(prjRecord.score_or_not == False,
                       prjRecord.prj_role == 'B',
                       prjRecord.prj_mem == name). \
                all()
            r3 = db.session.query(func.sum(prjRecord.score).label('Sum')). \
                filter(prjRecord.score_or_not == False,
                       prjRecord.prj_role == 'C',
                       prjRecord.prj_mem == name). \
                all()
            r4 = db.session.query(func.sum(prjRecord.score).label('Sum')). \
                filter(prjRecord.score_or_not == False,
                       prjRecord.prj_role == 'D',
                       prjRecord.prj_mem == name). \
                all()

            # 用户相关项目的编号列表
            r5 = db.session.query(prjRecord.prj_no).\
                filter(prjRecord.prj_mem == name).\
                all()
            # 展开并获取唯一的项目编号
            r5 = list(set(map(lambda x: str(x), list(chain(*r5)))))

            if r1[0].Sum is None:
                a1 = 0.0
            else:
                a1 = float(r1[0].Sum)
            if r2[0].Sum is None:
                a2 = 0.0
            else:
                a2 = float(r2[0].Sum)
            if r3[0].Sum is None:
                a3 = 0.0
            else:
                a3 = float(r3[0].Sum)
            if r4[0].Sum is None:
                a4 = 0.0
            else:
                a4 = float(r4[0].Sum)

            # 不显示没有分值的条目
            if a1 + a2 + a3 + a4 != 0.0:
                score_set.update({name: {'Initiator': a1,
                                         'Leader': a2,
                                         'Major': a3,
                                         'Minor': a4,
                                         'Sum': a1 + a2 + a3 + a4,
                                         'Remark': r5
                                         }
                                  })

        # 汇总
        def summary(d):
            Initiator_sum = 0
            Leader_sum    = 0
            Major_sum     = 0
            Minor_sum     = 0
            Sum_sum       = 0

            for e in d.values():
                Initiator_sum += e.get('Initiator')
                Leader_sum    += e.get('Leader')
                Major_sum     += e.get('Major')
                Minor_sum     += e.get('Minor')
                Sum_sum       += e.get('Sum')

            return dict(Initiator_sum=Initiator_sum,
                        Leader_sum=Leader_sum,
                        Major_sum=Major_sum,
                        Minor_sum=Minor_sum,
                        Sum_sum=Sum_sum)

        return score_set,summary(score_set)
