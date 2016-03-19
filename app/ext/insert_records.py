# -*- coding:utf-8 -*-
__author__ = 'Dearc'

from rules import ruleMaker

class insert_records(object):
    '''模块作用：向数据库插入操作的动作、分值来作为日志，供后续调用
       依赖模块：rules，从中获取点子分和项目积分的分值信息
       注意事项：务必注意分值信息的类型是否为int
    '''
    def __init__(self):
        '''从rules中获取分值信息'''
        self.rul = ruleMaker()
        self.rv = self.rul.rules_api_info()

    def prj_launch(self, golden_type=None, prj_num=None):
        prj_num_ = prj_num
        golden_type = golden_type

        if golden_type == 'S1':
            golden = int(self.rv['s1']['value'])
        elif golden_type == 'P1':
            golden = int(self.rv['p1']['value'])
        else:
            golden = 0

        insert_records = '''INSERT INTO MONTHLY_ACTION
                            (PROJECT_NUM,DATE,ACTION,SCORE)
                             VALUES ("%s",DATE('now'),"%s","%s");
                         ''' % (prj_num_, 'project launched', golden)
        return insert_records

    def insert_month_3_release(self, conn, prj_num, flag=None):
        flag_ = flag
        prj_num_ = prj_num
        con_ = conn

        tmp = '''SELECT GOLDEN_IDEA_LEVEL,PROJECT_SCORE_LEVEL
                 FROM SCORE_CARD
                 WHERE PROJECT_NUMBER = "%s"''' % (prj_num_)
        cur = con_.cursor()
        g, p = cur.execute(tmp).fetchall()[0]

        prj_score = {'S': int(self.rv['s']['value']),
                     'P': int(self.rv['p']['value']),
                     'K': int(self.rv['k']['value']),
                     'G': int(self.rv['g']['value']),
                     'B': int(self.rv['b']['value'])}

        golden_score = {'S1': 0,  # already added when prj launched
                        'P1': 0,  # already added when prj launched
                        'K1': int(self.rv['k1']['value']),
                        'G1': int(self.rv['g1']['value']),
                        'G2': int(self.rv['g2']['value']),
                        'G3': int(self.rv['g3']['value']),
                        'B1': int(self.rv['b1']['value']),
                        'B2': int(self.rv['b2']['value']),
                        'B3': int(self.rv['b3']['value'])}

        if flag_.endswith('checkpoint'):
            total = int(prj_score.get(p) * 0.5 + golden_score.get(g) * 0.5)
        if flag_.endswith('closed'):
            total = 0

        insert_records = '''INSERT INTO MONTHLY_ACTION
                            (PROJECT_NUM,DATE,ACTION,SCORE)
                            VALUES ("%s",DATE('now'),"%s","%s");
                         ''' % (prj_num_, flag_, total)

        cur.execute(insert_records)
        con_.commit()
