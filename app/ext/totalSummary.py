# -*- coding:utf-8 -*-

__author__ = 'Dearc'

from report_monthly import report_html


class totalSummary(object):
    """模块作用：查询 /search 页面数据，积分明细不提供模糊查询
       依赖：依赖rules提供分值分配信息
            依赖report_monthly 提供积分详细信息
    """

    def __init__(self, name):
        self.name = name

        self.SQL_PROJECT_TOTAL = '''SELECT COUNT(*)
                                    FROM TOTAL
                                    WHERE
                                    ININTIALOR LIKE "%%%s%%"
                                    OR LEADER LIKE "%%%s%%"
                                    OR MAJOR_PARTICIPATOR LIKE "%%%s%%"
                                    OR MINIOR_PARTICIPATOR LIKE "%%%s%%";
                                 ''' % (tuple([self.name]) * 4)

        # 追踪完成的项目，通过所有检查点
        self.SQL_PROJECT_FINISHED = '''SELECT COUNT(*)
                                       FROM TOTAL
                                       WHERE CHECK_POINT_3_MONTH = 1
                                       AND CHECK_POINT_6_MONTH = 1
                                       AND (
                                          ININTIALOR LIKE "%%%s%%"
                                          OR LEADER LIKE "%%%s%%"
                                          OR MAJOR_PARTICIPATOR LIKE "%%%s%%"
                                          OR MINIOR_PARTICIPATOR LIKE "%%%s%%"
                                       );''' % (tuple([self.name]) * 4)

        # 通过3个月的检查点，但未通过6个月检查点
        self.SQL_PROJECT_IN_3_MONTH = '''SELECT COUNT(*)
                                         FROM TOTAL
                                         WHERE CHECK_POINT_3_MONTH = 1
                                         AND CHECK_POINT_6_MONTH <> 1
                                         AND (
                                          ININTIALOR LIKE "%%%s%%"
                                          OR LEADER LIKE "%%%s%%"
                                          OR MAJOR_PARTICIPATOR LIKE "%%%s%%"
                                          OR MINIOR_PARTICIPATOR LIKE "%%%s%%"
                                         );''' % (tuple([self.name]) * 4)

        # 通过6个月检查点
        self.SQL_PROJECT_IN_6_MONTH = '''SELECT COUNT(*)
                                         FROM TOTAL
                                         WHERE CHECK_POINT_6_MONTH = 1
                                         AND (
                                          ININTIALOR LIKE "%%%s%%"
                                          OR LEADER LIKE "%%%s%%"
                                          OR MAJOR_PARTICIPATOR LIKE "%%%s%%"
                                          OR MINIOR_PARTICIPATOR LIKE "%%%s%%"
                                         );''' % (tuple([self.name]) * 4)

        # 没有通过检查点的项目
        self.SQL_PROJECT_FAILED = '''SELECT COUNT(*)
                                     FROM TOTAL
                                     WHERE CHECK_POINT_6_MONTH = 0
                                     AND (
                                      ININTIALOR LIKE "%%%s%%"
                                      OR LEADER LIKE "%%%s%%"
                                      OR MAJOR_PARTICIPATOR LIKE "%%%s%%"
                                      OR MINIOR_PARTICIPATOR LIKE "%%%s%%"
                                     );''' % (tuple([self.name]) * 4)

        # 项目发起者的项目总数
        self.SQL_ININTIALOR = '''SELECT COUNT(*)
                                 FROM TOTAL
                                 WHERE ININTIALOR LIKE "%%%s%%";
                              ''' % self.name

        # 项目领导者的总数
        self.SQL_LEADER = '''SELECT COUNT(*)
                             FROM TOTAL
                             WHERE LEADER LIKE "%%%s%%";
                          ''' % self.name

        # 作为项目主要成员的数目
        self.SQL_MAJOR = '''SELECT COUNT(*)
                            FROM TOTAL
                            WHERE MAJOR_PARTICIPATOR LIKE "%%%s%%";
                         ''' % self.name

        # 作为项目次要成员的数目
        self.SQL_MINIOR = '''SELECT COUNT(*)
                             FROM TOTAL
                             WHERE MINIOR_PARTICIPATOR LIKE "%%%s%%";
                          ''' % self.name

    def summary(self, conn):
        # 报表系统初始化,需要额外的参数
        report = report_html(conn=conn, month_begin=None, month_end=None)
        # 依据人名获取明细报告
        rv = report.summary(self.name)
        # 数据库游标
        cur  = conn.cursor()

        d0 = cur.execute(self.SQL_PROJECT_TOTAL).fetchone()[0]
        d1 = cur.execute(self.SQL_PROJECT_FINISHED).fetchone()[0]
        d2 = cur.execute(self.SQL_PROJECT_IN_3_MONTH).fetchone()[0]
        d3 = cur.execute(self.SQL_PROJECT_IN_6_MONTH).fetchone()[0]
        d4 = cur.execute(self.SQL_PROJECT_FAILED).fetchone()[0]
        d5 = cur.execute(self.SQL_ININTIALOR).fetchone()[0]
        d6 = cur.execute(self.SQL_MINIOR).fetchone()[0]
        d7 = cur.execute(self.SQL_LEADER).fetchone()[0]
        d9 = cur.execute(self.SQL_MAJOR).fetchone()[0]

        # 返回两个字典，注意后续解包
        return dict(d0=d0, d1=d1, d2=d2, d3=d3, d4=d4, d5=d5, d6=d6, d7=d7, d9=d9), rv
