# -*- coding:utf-8 -*-

__author__ = 'Dearc'

from rules import ruleMaker

class totalSummary(object):
    """模块作用：查询 /search 页面数据
       依赖：依赖rules提供分值分配信息
    """
    def __init__(self, name):
        # 初始化rules模块
        self.rul = ruleMaker()
        self.rv = self.rul.rules_api_info()

        # 还请务必注意来自self.rv中值的类型
        ini_s = float(self.rv['s']['distribution'][0])
        ini_p = float(self.rv['p']['distribution'][0])
        lea_p = float(self.rv['p']['distribution'][1])
        maj_p = float(self.rv['p']['distribution'][2])
        min_p = float(self.rv['p']['distribution'][3])

        self.name = name
        self.SQL_PROJECT_TOTAL = '''SELECT COUNT(*)
                                   FROM TOTAL
                                   WHERE
                                   ININTIALOR LIKE "%%%s%%"
                                   OR LEADER LIKE "%%%s%%"
                                   OR MAJOR_PARTICIPATOR LIKE "%%%s%%"
                                   OR MINIOR_PARTICIPATOR LIKE "%%%s%%";
                                ''' % (tuple([self.name]) * 4)

        self.SQL_PROJECT_FINISHED = '''SELECT COUNT(*)
                                      FROM TOTAL
                                      WHERE CHECK_POINT_3_MONTH = 1
                                      AND CHECK_POINT_3_MONTH = 1
                                      AND (
                                          ININTIALOR LIKE "%%%s%%"
                                          OR LEADER LIKE "%%%s%%"
                                          OR MAJOR_PARTICIPATOR LIKE "%%%s%%"
                                          OR MINIOR_PARTICIPATOR LIKE "%%%s%%"
                                      );''' % (tuple([self.name]) * 4)

        self.SQL_PROJECT_IN_3_MONTH = '''SELECT COUNT(*)
                                        FROM TOTAL
                                        WHERE CHECK_POINT_3_MONTH = 1
                                        AND CHECK_POINT_3_MONTH <> 1
                                        AND (
                                          ININTIALOR LIKE "%%%s%%"
                                          OR LEADER LIKE "%%%s%%"
                                          OR MAJOR_PARTICIPATOR LIKE "%%%s%%"
                                          OR MINIOR_PARTICIPATOR LIKE "%%%s%%"
                                        );''' % (tuple([self.name]) * 4)

        self.SQL_PROJECT_IN_6_MONTH = '''SELECT COUNT(*)
                                        FROM TOTAL
                                        WHERE CHECK_POINT_6_MONTH = 1
                                        AND (
                                          ININTIALOR LIKE "%%%s%%"
                                          OR LEADER LIKE "%%%s%%"
                                          OR MAJOR_PARTICIPATOR LIKE "%%%s%%"
                                          OR MINIOR_PARTICIPATOR LIKE "%%%s%%"
                                        );''' % (tuple([self.name]) * 4)

        self.SQL_PROJECT_FAILED = '''SELECT COUNT(*)
                                        FROM TOTAL
                                        WHERE CHECK_POINT_6_MONTH = 0
                                        AND (
                                          ININTIALOR LIKE "%%%s%%"
                                          OR LEADER LIKE "%%%s%%"
                                          OR MAJOR_PARTICIPATOR LIKE "%%%s%%"
                                          OR MINIOR_PARTICIPATOR LIKE "%%%s%%"
                                        );''' % (tuple([self.name]) * 4)

        self.SQL_ININTIALOR = '''SELECT COUNT(*)
                                 FROM TOTAL
                                 WHERE ININTIALOR LIKE "%%%s%%";
                              ''' % self.name

        self.SQL_ININTIALOR_BONUS_S = '''SELECT SUM(ACTIVE_SCORE * %s)
                                         FROM TOTAL
                                         WHERE ININTIALOR LIKE "%%%s%%"
                                         AND PROJECT_SCORE_LEVEL = "S";
                                         ''' % (ini_s,self.name)

        self.SQL_ININTIALOR_BONUS_P = '''SELECT SUM(ACTIVE_SCORE * %s)
                                         FROM TOTAL
                                         WHERE ININTIALOR LIKE "%%%s%%"
                                         AND (PROJECT_SCORE_LEVEL = "P"
                                              OR PROJECT_SCORE_LEVEL = "K"
                                              OR PROJECT_SCORE_LEVEL = "G"
                                              OR PROJECT_SCORE_LEVEL = "B");
                                         ''' % (ini_p,self.name)

        self.SQL_LEADER = '''SELECT COUNT(*)
                                 FROM TOTAL
                                 WHERE LEADER LIKE "%%%s%%";
                              ''' % self.name

        self.SQL_LEADER_BONUS_P = '''SELECT SUM(ACTIVE_SCORE * %s)
                                         FROM TOTAL
                                         WHERE LEADER LIKE "%%%s%%"
                                         AND (PROJECT_SCORE_LEVEL = "P"
                                              OR PROJECT_SCORE_LEVEL = "K"
                                              OR PROJECT_SCORE_LEVEL = "G"
                                              oR PROJECT_SCORE_LEVEL = "B");
                                         ''' % (lea_p,self.name)

        self.SQL_MAJOR = '''SELECT COUNT(*)
                                 FROM TOTAL
                                 WHERE MAJOR_PARTICIPATOR LIKE "%%%s%%";
                              ''' % self.name

        self.SQL_MAJOR_BONUS = '''SELECT SUM(ACTIVE_SCORE * %s / MAJOR_PARTICIPATOR_COUNT)
                                  FROM TOTAL
                                  WHERE MAJOR_PARTICIPATOR LIKE "%%%s%%";
                                  ''' % (maj_p,self.name)

        self.SQL_MINIOR = '''SELECT COUNT(*)
                                 FROM TOTAL
                                 WHERE MINIOR_PARTICIPATOR LIKE "%%%s%%";
                              ''' % self.name

        self.SQL_MINIOR_BONUS = '''SELECT SUM(ACTIVE_SCORE * %s / MINIOR_PARTICIPATOR_COUNT)
                                  FROM TOTAL
                                  WHERE MINIOR_PARTICIPATOR LIKE "%%%s%%";
                                  ''' % (min_p,self.name)

    def summary(self, conn):
        conn = conn
        cur = conn.cursor()
        d0 = cur.execute(self.SQL_PROJECT_TOTAL).fetchone()[0]
        d1 = cur.execute(self.SQL_PROJECT_FINISHED).fetchone()[0]
        d2 = cur.execute(self.SQL_PROJECT_IN_3_MONTH).fetchone()[0]
        d3 = cur.execute(self.SQL_PROJECT_IN_6_MONTH).fetchone()[0]
        d4 = cur.execute(self.SQL_PROJECT_FAILED).fetchone()[0]
        d5 = cur.execute(self.SQL_ININTIALOR).fetchone()[0]
        d6_1 = cur.execute(self.SQL_ININTIALOR_BONUS_S).fetchone()[0]
        d6_2 = cur.execute(self.SQL_ININTIALOR_BONUS_P).fetchone()[0]

        if d6_1 is not None:
            if d6_2 is not None:
                d6 = round(d6_1 + d6_2,1)
            else:
                d6 = round(d6_1,1)
        if d6_1 is None:
            if d6_2 is not None:
                d6 = round(d6_2,1)
            else:
                d6 = 0

        d7 = cur.execute(self.SQL_LEADER).fetchone()[0]
        d8 = cur.execute(self.SQL_LEADER_BONUS_P).fetchone()[0]
        if d8 is None:d8 = 0
        d9 = cur.execute(self.SQL_MAJOR).fetchone()[0]
        d10 = cur.execute(self.SQL_MAJOR_BONUS).fetchone()[0]
        if d10 is None:d10 = 0
        d11 = cur.execute(self.SQL_MINIOR).fetchone()[0]
        d12 = cur.execute(self.SQL_MINIOR_BONUS).fetchone()[0]
        if d12 is None:d12 = 0
        d14 = round(d6+d8+d10+d12,1)

        return dict(d0=d0,
					d1=d1,
					d2=d2,
					d3=d3,
					d4=d4,
					d5=d5,
					d7=d7,
					d9=d9,
					d11=d11,
					d6=round(d6,1),
					d8=round(d8,1),
					d10=round(d10,1),
					d12=round(d12,1),
					d14=d14)