# -*- coding:utf-8 -*-

__author__ = 'Dearc'

from rules import ruleMaker

class totalSummary(object):
    """模块作用：查询 /search 页面数据，积分明细不提供模糊查询
       依赖：依赖rules提供分值分配信息
            依赖report_monthly 提供积分详细信息
    """

    def __init__(self, name):
        self.name = name
        self.rv = ruleMaker().rules_api_info()

    def personal_score_matrix(self,conn=None):
        cur = conn.cursor()
        score_matrix_sql = '''SELECT [PROJECT_NUMBER],
                                     [PROJECT_SCORE_LEVEL],
                                     [TOTAL_SCORE],
                                     [ACTIVE_SCORE],
                                     [ININTIALOR],
                                     [LEADER],
                                     [MAJOR_PARTICIPATOR],
                                     [MAJOR_PARTICIPATOR_COUNT],
                                     [MINIOR_PARTICIPATOR],
                                     [MINIOR_PARTICIPATOR_COUNT]
                              FROM [TOTAL]
                              WHERE ININTIALOR="%s"
                              OR LEADER="%s"
                              OR [MAJOR_PARTICIPATOR] LIKE "%%%s%%"
                              OR [MINIOR_PARTICIPATOR] LIKE "%%%s%%"''' % (self.name,self.name,self.name,self.name)
        res = cur.execute(score_matrix_sql).fetchall()

        rs = []
        for elements in res:

            pj_num = elements[0]
            pj_type = elements[1]
            cis_score = elements[2]
            active_score = elements[3]

            def score(active=False):
                staff_score = []

                l = lambda active:active_score if active else cis_score

                if self.name in elements[4]:
                    staff_score.append(l(active) * eval(self.rv[pj_type.lower()]['distribution'][0]))
                if self.name in elements[5]:
                    staff_score.append(l(active) * eval(self.rv[pj_type.lower()]['distribution'][1]))
                if self.name in elements[6]:
                    staff_score.append(l(active) * eval(self.rv[pj_type.lower()]['distribution'][2])/elements[7])
                if self.name in elements[8]:
                    staff_score.append(l(active) * eval(self.rv[pj_type.lower()]['distribution'][3])/elements[9])
                return sum(staff_score)

            def check_point_score():
                if pj_type == 'S' or pj_type == 'P':
                    return [score(False),0,0]
                else:
                    return [0,score(False)*eval(self.rv['check_3']),score(False)*eval(self.rv['check_6'])]

            r = [pj_num,pj_type,cis_score,score(False),score(True),score(False)-score(True)]
            r.extend(check_point_score())
            rs.append(r)

        total_score = []
        available_score = []
        inactive_score = []
        for lst in rs:
            total_score.append(lst[3])
            available_score.append(lst[4])
            inactive_score.append(lst[5])
        return rs,{'a':sum(total_score),'b':sum(available_score),'c':sum(inactive_score)}
