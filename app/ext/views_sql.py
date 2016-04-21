#-*- coding:utf-8 -*-
import bisect
from rules import ruleMaker

class views_sql(object):
    '''模块作用：视图函数用到的查询、插入、更新'''
    def __init__(self):
        self.SQL_SEARCH_MEMBER = '''SELECT PROJECT_NUMBER,
                                          PROJECT_NAME,
                                          PROJECT_DUE_TIME,
                                          ININTIALOR,
                                          LEADER,
                                          MAJOR_PARTICIPATOR,
                                          MINIOR_PARTICIPATOR,
                                          GOLDEN_IDEA_SCORE,
                                          PROJECT_SCORE,
                                          ACTIVE_SCORE
                                   FROM TOTAL
                                   WHERE LEADER LIKE "%%%s%%"
                                   OR ININTIALOR LIKE "%%%s%%"
                                   OR MINIOR_PARTICIPATOR LIKE "%%%s%%"
                                   OR MAJOR_PARTICIPATOR LIKE "%%%s%%";
                                '''
        # 注意，在检查点前2天，后30天检查 (-30,+2)
        self.data_3_month = '''SELECT PROJECT_NUMBER,
                                      PROJECT_NAME,
                                      CHECK_POINT_3_MONTH,
                                      LEADER,
                                      GOLDEN_IDEA_SCORE,
                                      PROJECT_SCORE,
                                      TARGET_SCORE,
                                      ACTIVE_SCORE
                                  FROM TOTAL
                                  WHERE DATE('now','-30 days') < CHECK_POINT_3_MONTH
                                  AND DATE('now','+2 days') > CHECK_POINT_3_MONTH
                                  AND ([3_MONTH_CHECK] != 1 OR [3_MONTH_CHECK] IS NULL);
                               '''

        self.data_6_month = '''SELECT PROJECT_NUMBER,
                                      PROJECT_NAME,
                                      CHECK_POINT_6_MONTH,
                                      LEADER,
                                      GOLDEN_IDEA_SCORE,
                                      PROJECT_SCORE,
                                      TARGET_SCORE,
                                      ACTIVE_SCORE
                              FROM TOTAL
                              WHERE DATE('now','-30 days') < CHECK_POINT_6_MONTH
                              AND DATE('now','+2 days') > CHECK_POINT_6_MONTH
                              AND ([6_MONTH_CHECK] != 1 OR [6_MONTH_CHECK] IS NULL );'''

        self.UPDATE_PROJECT_INFO = '''UPDATE PROJECT_INFO
                                      SET PROJECT_NAME = "%s",PROJECT_DUE_TIME = "%s"
                                      WHERE PROJECT_NUMBER = "%s";'''

        self.UPDATE_MEMBER_INFO = '''UPDATE MEMBER_INFO
                                        SET ININTIALOR = "%s",
                                            LEADER = "%s",
                                            MAJOR_PARTICIPATOR = "%s",
                                            MINIOR_PARTICIPATOR = "%s",
                                            MAJOR_PARTICIPATOR_COUNT = "%s",
                                            MINIOR_PARTICIPATOR_COUNT = "%s"
                                        WHERE PROJECT_NUMBER = "%s";
                                        '''

        self.UPDATE_SCORE_INFO = ''' UPDATE SCORE_CARD
                                     SET GOLDEN_IDEA_LEVEL = "%s",
                                         PROJECT_SCORE_LEVEL = "%s",
                                         GOLDEN_IDEA_SCORE = "%s",
                                         PROJECT_SCORE = "%s",
                                         TARGET_SCORE = "%s",
                                         DUPLICABILITY = "%s",
                                         RESOURCE_USAGE = "%s",
                                         IMPLEMENT_PERIOD ="%s",
                                         KPI_IMPACT = "%s",
                                         COST_SAVING = "%s",
                                         ACTIVE_SCORE = "%s"
                                     WHERE PROJECT_NUMBER = "%s";
                                        '''

        self.INSERT_PROJECT_INFO = '''INSERT INTO
                                         PROJECT_INFO (PROJECT_NUMBER,PROJECT_NAME,PROJECT_DUE_TIME)
                                         VALUES ("%s","%s","%s");
                                         '''

        self.INSERT_MEMBER_INFO = '''INSERT INTO
                                        MEMBER_INFO (PROJECT_NUMBER,
                                                     ININTIALOR,
                                                     LEADER,
                                                     MAJOR_PARTICIPATOR,
                                                     MINIOR_PARTICIPATOR,
                                                     MAJOR_PARTICIPATOR_COUNT,
                                                     MINIOR_PARTICIPATOR_COUNT)
                                        VALUES ("%s","%s","%s","%s","%s","%s","%s");
                                        '''

        self.INSERT_SCORE_INFO = ''' INSERT INTO
                                     SCORE_CARD (PROJECT_NUMBER,
                                                 GOLDEN_IDEA_LEVEL,
                                                 PROJECT_SCORE_LEVEL,
                                                 GOLDEN_IDEA_SCORE,
                                                 PROJECT_SCORE,
                                                 TARGET_SCORE,
                                                 DUPLICABILITY,
                                                 RESOURCE_USAGE,
                                                 IMPLEMENT_PERIOD,
                                                 KPI_IMPACT,
                                                 COST_SAVING,
                                                 ACTIVE_SCORE)
                                     VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s");'''

        self.SEARCH_NAME = '''SELECT FORMAT_NAME
                     FROM USER_ID
                     WHERE NAME
                     LIKE "%%%s%%"
                     OR
                     ID LIKE "%%%s%%";'''

        self.SEARCH_PRJ_INFO = '''SELECT PROJECT_NUMBER,PROJECT_NAME,PROJECT_DUE_TIME,ININTIALOR,LEADER,MAJOR_PARTICIPATOR,
                                         MINIOR_PARTICIPATOR,PROJECT_SCORE_LEVEL,ACTIVE_SCORE
                                  FROM TOTAL
                                  WHERE PROJECT_NUMBER = "%s";'''

    def golden_type_judging(self,data):
        pass
