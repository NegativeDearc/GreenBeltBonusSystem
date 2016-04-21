#-*- coding:utf-8 -*-
__author__ = 'Dearc'

from rules import ruleMaker

class Action(object):
    '''模块作用：在admin面板中提供到达检查点的项目显示，周期为(-2，+30)
    '''
    def __init__(self,conn,project_num,flag = {'3_MONTH','6_MONTH'}):
        self.conn = conn
        self.project_num = project_num
        self.checkpoint = flag
        self.rul = ruleMaker()
        self.rv = self.rul.rules_api_info()

        # 检查项目类型
        self.PROJECT_TYPE = '''SELECT PROJECT_SCORE_LEVEL
                               FROM SCORE_CARD
                               WHERE PROJECT_NUMBER = "%s";
                            ''' % self.project_num
        # 检查3个月检查点
        self.MONTH_3_CHECK = '''SELECT [3_MONTH_CHECK]
                                FROM PROJECT_INFO
                                WHERE PROJECT_NUMBER = "%s";
                             ''' % self.project_num
        # 检查6个月检查点
        self.MONTH_6_CHECK = '''SELECT [6_MONTH_CHECK]
                                FROM PROJECT_INFO
                                WHERE PROJECT_NUMBER = "%s";
                             ''' % self.project_num
        # S/P类型的直接释放，无须节点
        self.UPDATE_ACTIVE_SCORE_0 = '''UPDATE SCORE_CARD
                                        SET ACTIVE_SCORE = TOTAL_SCORE
                                        WHERE PROJECT_NUMBER = "%s";
                                   ''' % self.project_num
        # 非S/P类型的3个月释放
        self.UPDATE_ACTIVE_SCORE_1 = '''UPDATE SCORE_CARD
                                        SET ACTIVE_SCORE = TOTAL_SCORE * %s + ACTIVE_SCORE
                                        WHERE PROJECT_NUMBER = "%s";
                                     ''' % (self.rv['check_3'],self.project_num)
        # 非S/P类型的6个月释放
        self.UPDATE_ACTIVE_SCORE_2 = '''UPDATE SCORE_CARD
                                        SET ACTIVE_SCORE = TOTAL_SCORE * %s + ACTIVE_SCORE
                                        WHERE PROJECT_NUMBER = "%s";
                                     ''' % (self.rv['check_6'],self.project_num)
        # 更新3个月检查点
        self.UPDATE_3_MONTH_CHECK_POINT = '''UPDATE PROJECT_INFO
                                             SET [3_MONTH_CHECK] = 1
                                             WHERE PROJECT_NUMBER = "%s";
                                          ''' % self.project_num
        # 更新6个月检查点
        self.UPDATE_6_MONTH_CHECK_POINT = '''UPDATE PROJECT_INFO
                                             SET [6_MONTH_CHECK] = 1
                                             WHERE PROJECT_NUMBER = "%s";
                                          ''' % self.project_num

    def release_bonus(self):
        ''''release bonus or close bonus'''
        cur = self.conn.cursor()
        # 获得项目类型
        pj_type = cur.execute(self.PROJECT_TYPE).fetchone()[0]

        if pj_type in ['K','G','B']:
            if self.checkpoint == '3_MONTH':
                if cur.execute(self.MONTH_3_CHECK).fetchone()[0] is None \
                or cur.execute(self.MONTH_3_CHECK).fetchone()[0] != 1:
                    cur.execute(self.UPDATE_ACTIVE_SCORE_1)
                    cur.execute(self.UPDATE_3_MONTH_CHECK_POINT)
                    self.conn.commit()
            if self.checkpoint == '6_MONTH':
                if cur.execute(self.MONTH_3_CHECK).fetchone()[0] is None \
                or cur.execute(self.MONTH_3_CHECK).fetchone()[0] != 1:
                    cur.execute(self.UPDATE_ACTIVE_SCORE_2)
                    cur.execute(self.UPDATE_6_MONTH_CHECK_POINT)
                    self.conn.commit()

    def close_prj(self):
        cur = self.conn.cursor()
        cur.execute(self.UPDATE_3_MONTH_CHECK_POINT)
        cur.execute(self.UPDATE_6_MONTH_CHECK_POINT)
        self.conn.commit()