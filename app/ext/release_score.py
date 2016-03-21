#-*- coding:utf-8 -*-
__author__ = 'Dearc'

class Action(object):
    '''模块作用：在admin面板中提供到达检查点的项目显示，周期为(-2，+30)
    '''
    def __init__(self,conn,project_num,flag = ['3_MONTH','6_MONTH']):
        self.conn = conn
        self.project_num = project_num
        self.checkpoint = flag

        self.PROJECT_TYPE = '''SELECT PROJECT_SCORE_LEVEL
                               FROM SCORE_CARD
                               WHERE PROJECT_NUMBER = "%s";
                            ''' % self.project_num

        self.MONTH_3_CHECK = '''SELECT [3_MONTH_CHECK]
                                FROM PROJECT_INFO
                                WHERE PROJECT_NUMBER = "%s";
                             ''' % self.project_num

        self.MONTH_6_CHECK = '''SELECT [6_MONTH_CHECK]
                                FROM PROJECT_INFO
                                WHERE PROJECT_NUMBER = "%s";
                             ''' % self.project_num

        self.UPDATE_ACTIVE_SCORE = '''UPDATE SCORE_CARD
                                      SET ACTIVE_SCORE = PROJECT_SCORE/2 + ACTIVE_SCORE
                                      WHERE PROJECT_NUMBER = "%s";
                                   ''' % self.project_num

        self.UPDATE_ACTIVE_SCORE_2 = '''UPDATE SCORE_CARD
                                        SET ACTIVE_SCORE = (GOLDEN_IDEA_SCORE + PROJECT_SCORE)/2 + ACTIVE_SCORE
                                        WHERE PROJECT_NUMBER = "%s";
                                     ''' % self.project_num


        self.UPDATE_3_MONTH_CHECK_POINT = '''UPDATE PROJECT_INFO
                                             SET [3_MONTH_CHECK] = 1
                                             WHERE PROJECT_NUMBER = "%s";
                                          ''' % self.project_num

        self.UPDATE_6_MONTH_CHECK_POINT = '''UPDATE PROJECT_INFO
                                             SET [6_MONTH_CHECK] = 1
                                             WHERE PROJECT_NUMBER = "%s";
                                          ''' % self.project_num


    def release_bonus(self):
        ''''release bonus or close bonus'''
        con = self.conn
        cur = con.cursor()

        pj_type = cur.execute(self.PROJECT_TYPE).fetchone()[0]

        if pj_type == 'S' or pj_type == 'P':
            if self.checkpoint == '3_MONTH':
                if cur.execute(self.MONTH_3_CHECK).fetchone()[0] is None \
                or cur.execute(self.MONTH_3_CHECK).fetchone()[0] != 1:
                    cur.execute(self.UPDATE_ACTIVE_SCORE)
                    cur.execute(self.UPDATE_3_MONTH_CHECK_POINT)
                    con.commit()
            if self.checkpoint == '6_MONTH':
                if cur.execute(self.MONTH_6_CHECK).fetchone()[0] is None \
                or cur.execute(self.MONTH_6_CHECK).fetchone()[0] != 1:
                    cur.execute(self.UPDATE_ACTIVE_SCORE)
                    cur.execute(self.UPDATE_6_MONTH_CHECK_POINT)
                    con.commit()

        if pj_type in ['K','G','B']:
            if self.checkpoint == '3_MONTH':
                if cur.execute(self.MONTH_3_CHECK).fetchone()[0] is None \
                or cur.execute(self.MONTH_3_CHECK).fetchone()[0] != 1:
                    cur.execute(self.UPDATE_ACTIVE_SCORE_2)
                    cur.execute(self.UPDATE_3_MONTH_CHECK_POINT)
                    con.commit()
            if self.checkpoint == '6_MONTH':
                if cur.execute(self.MONTH_3_CHECK).fetchone()[0] is None \
                or cur.execute(self.MONTH_3_CHECK).fetchone()[0] != 1:
                    cur.execute(self.UPDATE_ACTIVE_SCORE_2)
                    cur.execute(self.UPDATE_6_MONTH_CHECK_POINT)
                    con.commit()

    def close_prj(self):
        con = self.conn
        cur = con.cursor()
        cur.execute(self.UPDATE_3_MONTH_CHECK_POINT)
        cur.execute(self.UPDATE_6_MONTH_CHECK_POINT)
        con.commit()