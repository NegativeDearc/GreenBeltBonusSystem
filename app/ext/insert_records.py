# -*- coding:utf-8 -*-
__author__ = 'Dearc'

from rules import ruleMaker

class insert_records(object):
    '''模块作用：向数据库插入操作的动作、分值来作为日志，供后续调用
       依赖模块：rules，从中获取点子分和项目积分的分值信息
       注意事项：务必注意分值信息的类型是否为int/float
    '''
    def __init__(self):
        '''从rules中获取分值信息'''
        self.rul = ruleMaker()
        self.rv  = self.rul.rules_api_info()

    def prj_launch(self, golden_type=None, prj_num=None,conn = None):
        # 初始化游标
        cur = conn.cursor()
        # 查询语句
        target_score_sql = '''SELECT TARGET_SCORE
                              FROM [SCORE_CARD]
                              WHERE PROJECT_NUMBER = "%s"''' % prj_num
        # 结果，一般不为None
        target_score = cur.execute(target_score_sql).fetchone()[0]
        # S/P 类型在项目起始直接释放golden score，后续如何改动？
        if golden_type == 'S1':
            golden = int(self.rv['s1']['value'])
        elif golden_type == 'P1':
            golden = int(self.rv['p1']['value'])
        else:
            golden = 0

        res = target_score + golden

        insert_records = '''INSERT INTO MONTHLY_ACTION
                            (PROJECT_NUM,DATE,ACTION,SCORE)
                            VALUES ("%s",DATE('now'),"%s","%s");
                         ''' % (prj_num, 'project launched', res)

        cur.execute(insert_records)
        conn.commit()

    def insert_release_detail(self, conn, prj_num, flag={1,2,3,4}):
        '''
        flag = 1 ->3 month release
        flag = 2 ->6 month release
        flag = 3 ->3 month closed
        flag = 4 ->6 month closed
        '''
        # 查询点子类型和项目类型
        tmp = '''SELECT GOLDEN_IDEA_LEVEL,PROJECT_SCORE_LEVEL
                 FROM SCORE_CARD
                 WHERE PROJECT_NUMBER = "%s"''' % prj_num
        # 游标
        cur = conn.cursor()
        # 解包
        g, p = cur.execute(tmp).fetchall()[0]
        # 获取配置的分值信息
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

        # 这里，需根据配置决定每个检查点释放的比例
        flag_description = None
        total = None
        # 3个月释放
        if flag == 1:
            flag_description = '3 month release'
            total = int(prj_score.get(p) * float(self.rv['p_3']) + golden_score.get(g) * float(self.rv['g_3']))
        # 6个月释放
        if flag == 2:
            flag_description = '6 month release'
            total = int(prj_score.get(p) * float(self.rv['p_6']) + golden_score.get(g) * float(self.rv['g_6']))
        # 3个月未通过关闭，不得分
        if flag == 3:
            flag_description = '3 month closed'
            total = 0
        # 6个月未通过关闭，不得分
        if flag == 4:
            flag_description = '6 month closed'
            total = 0

        # 如何将flag从数值转为说明
        insert_records = '''INSERT INTO MONTHLY_ACTION
                            (PROJECT_NUM,DATE,ACTION,SCORE)
                            VALUES ("%s",DATE('now'),"%s","%s");
                         ''' % (prj_num,flag_description, total)

        cur.execute(insert_records)
        conn.commit()