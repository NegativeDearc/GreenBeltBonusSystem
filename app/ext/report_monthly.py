# -*- coding:utf-8 -*-
__author__ = 'SXChen'

from itertools import chain
from rules import ruleMaker

class report_html(object):
    '''模块作用：为/report页面提供查询
       依赖模块：依赖rules为其提供成员分配比例
       --为什么不从totalSummary中继承？
       --因为totalSummary来自total表，而本模块来自report表，
         若分值出了问题，可以明显发觉。只有两张表的数据统一了，才能说明分值无误
    '''
    def __init__(self,conn,month_begin,month_end):
        # 初始化rules模块
        self.rul = ruleMaker()
        self.rv = self.rul.rules_api_info()
        self.conn = conn
        # 潜在的bug 若month_begin > month_end 就会出错
        self.month_begin = month_begin
        self.month_end = month_end
    def get_name(self):
        query_member = '''SELECT ININTIALOR,LEADER,MAJOR_PARTICIPATOR,MINIOR_PARTICIPATOR
                          FROM REPORT
                          WHERE DATE > "%s"
                          AND DATE < "%s";
                       ''' % (self.month_begin,self.month_end)

        cur = self.conn.cursor()
        member = cur.execute(query_member).fetchall()
        # use RegExp to make sure the name string can be split correctly
        # lambda x:re.split('\s*,\s*',x)
        # 用集合保持人名的唯一性
        rv = set(chain(*map(lambda x:x.split(', '),list(chain(*member)))))
        return rv
    def summary(self,name):
        name = name
        # 还请务必注意来自self.rv中值的类型
        ini_s = float(self.rv['s']['distribution'][0])
        ini_p = float(self.rv['p']['distribution'][0])
        lea_p = float(self.rv['p']['distribution'][1])
        maj_p = float(self.rv['p']['distribution'][2])
        min_p = float(self.rv['p']['distribution'][3])

        SQL_ININTIALOR_BONUS_S = '''SELECT SUM(SCORE * %s)
                                     FROM REPORT
                                     WHERE ININTIALOR LIKE "%%%s%%"
                                     AND PROJECT_SCORE_LEVEL = "S";
                                     ''' % (ini_s,name)

        SQL_ININTIALOR_BONUS_P = '''SELECT SUM(SCORE * %s)
                                     FROM REPORT
                                     WHERE ININTIALOR LIKE "%%%s%%"
                                     AND (PROJECT_SCORE_LEVEL = "S"
                                          OR PROJECT_SCORE_LEVEL = "P"
                                          OR PROJECT_SCORE_LEVEL = "K"
                                          OR PROJECT_SCORE_LEVEL = "G"
                                          OR PROJECT_SCORE_LEVEL = "B");
                                     ''' % (ini_p,name)

        SQL_LEADER_BONUS_P = '''SELECT SUM(SCORE * %s)
                                         FROM REPORT
                                         WHERE LEADER LIKE "%%%s%%"
                                         AND (PROJECT_SCORE_LEVEL = "P"
                                              OR PROJECT_SCORE_LEVEL = "K"
                                              OR PROJECT_SCORE_LEVEL = "G"
                                              oR PROJECT_SCORE_LEVEL = "B");
                                         ''' % (lea_p,name)


        SQL_MAJOR_BONUS = '''SELECT SUM(SCORE * %s / MAJOR_PARTICIPATOR_COUNT)
                                  FROM REPORT
                                  WHERE MAJOR_PARTICIPATOR LIKE "%%%s%%";
                                  ''' % (maj_p,name)

        SQL_MINIOR_BONUS = '''SELECT SUM(SCORE * %s / MINIOR_PARTICIPATOR_COUNT)
                              FROM REPORT
                              WHERE MINIOR_PARTICIPATOR LIKE "%%%s%%";
                                  ''' % (min_p,name)

        cur = self.conn.cursor()

        initiator_bonus_s = cur.execute(SQL_ININTIALOR_BONUS_S).fetchone()[0]
        if initiator_bonus_s is None:
            initiator_bonus_s = 0
        initiator_bonus_p = cur.execute(SQL_ININTIALOR_BONUS_P).fetchone()[0]
        if initiator_bonus_p is None:
            initiator_bonus_p = 0
        leader_bonus = cur.execute(SQL_LEADER_BONUS_P).fetchone()[0]
        if leader_bonus is None:
            leader_bonus = 0
        major_bonus = cur.execute(SQL_MAJOR_BONUS).fetchone()[0]
        if major_bonus is None:
            major_bonus = 0
        minor_bonus = cur.execute(SQL_MINIOR_BONUS).fetchone()[0]
        if minor_bonus is None:
            minor_bonus = 0

        r = {'Initiator':round(initiator_bonus_s + initiator_bonus_p,1),
             'Leader':round(leader_bonus,1),
             'Major':round(major_bonus,1),
             'Minor':round(minor_bonus,1),
             'sum':round(initiator_bonus_s+initiator_bonus_p+leader_bonus+major_bonus+minor_bonus,1)
             }
        return r

    def prj_set(self,name):
        '''查询与人名相关的唯一项目编号，供html折叠显示'''
        name = name
        cur = self.conn.cursor()

        SQL_SELECT_PRJ_SET = '''SELECT DISTINCT PROJECT_NUM
                                FROM REPORT
                                WHERE ININTIALOR LIKE "%%%s%%"
                                OR LEADER LIKE "%%%s%%"
                                OR MAJOR_PARTICIPATOR LIKE "%%%s%%"
                                OR MINIOR_PARTICIPATOR LIKE "%%%s%%"
                             ''' % (name,name,name,name)

        rv = cur.execute(SQL_SELECT_PRJ_SET).fetchall()
        return rv