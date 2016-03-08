# -*- coding:utf-8 -*-
__author__ = 'Dearc'


class insert_records:
    def __init__(self):
        pass

    def prj_launch(self, golden_type=None, prj_num=None):
        prj_num_ = prj_num
        golden_type = golden_type

        if golden_type == 'S1':
            golden = 100
        elif golden_type == 'P1':
            golden = 200
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

        prj_score = {'S': 200,
                     'P': 800,
                     'K': 1500,
                     'G': 2500,
                     'B': 3500}

        golden_score = {'S1': 0,  # already added when prj launched
                        'P1': 0,  # already added when prj launched
                        'K1': 500,
                        'G1': 800,
                        'G2': 1000,
                        'G3': 1500,
                        'B1': 2000,
                        'B2': 3000,
                        'B3': 4000}

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
