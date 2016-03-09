__author__ = 'SXChen'

from itertools import chain

class report_html:
    def __init__(self,conn,month_begin,month_end):
        self.conn = conn
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
        rv = set(chain(*map(lambda x:x.split(', '),list(chain(*member)))))
        return rv
    
    def summary(self,name):
        name = name

        SQL_ININTIALOR_BONUS_S = '''SELECT SUM(SCORE * 0.5)
                                     FROM REPORT
                                     WHERE ININTIALOR LIKE "%%%s%%"
                                     AND PROJECT_SCORE_LEVEL = "S";
                                     ''' % name

        SQL_ININTIALOR_BONUS_P = '''SELECT SUM(SCORE * 0.2)
                                     FROM REPORT
                                     WHERE ININTIALOR LIKE "%%%s%%"
                                     AND (PROJECT_SCORE_LEVEL = "S"
                                          OR PROJECT_SCORE_LEVEL = "P"
                                          OR PROJECT_SCORE_LEVEL = "K"
                                          OR PROJECT_SCORE_LEVEL = "G"
                                          OR PROJECT_SCORE_LEVEL = "B");
                                     ''' % name

        SQL_LEADER_BONUS_P = '''SELECT SUM(SCORE * 0.3)
                                         FROM REPORT
                                         WHERE LEADER LIKE "%%%s%%"
                                         AND (PROJECT_SCORE_LEVEL = "P"
                                              OR PROJECT_SCORE_LEVEL = "K"
                                              OR PROJECT_SCORE_LEVEL = "G"
                                              oR PROJECT_SCORE_LEVEL = "B");
                                         ''' % name


        SQL_MAJOR_BONUS = '''SELECT SUM(SCORE * 0.4 / MAJOR_PARTICIPATOR_COUNT)
                                  FROM REPORT
                                  WHERE MAJOR_PARTICIPATOR LIKE "%%%s%%";
                                  ''' % name

        SQL_MINIOR_BONUS = '''SELECT SUM(SCORE * 0.1 / MINIOR_PARTICIPATOR_COUNT)
                              FROM REPORT
                              WHERE MINIOR_PARTICIPATOR LIKE "%%%s%%";
                                  ''' % name

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











