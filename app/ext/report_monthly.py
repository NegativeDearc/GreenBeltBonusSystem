# -*- coding:utf-8 -*-
__author__ = 'SXChen'

from itertools import chain
from rules import ruleMaker

class report_html(object):
    '''模块作用：为/report页面提供*精确*的人名查询，
               如果是模糊查找，那么在/search页面会有记录产生，
               但无法提供积分的项目细节
       依赖模块：依赖rules为其提供成员分配比例
       本模块是产生明细的唯一模块，需十分仔细！
    '''
    def __init__(self,conn,month_begin,month_end):
        # 初始化rules模块，获取参数配置
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
        ini_k = float(self.rv['k']['distribution'][0])
        ini_g = float(self.rv['g']['distribution'][0])
        ini_b = float(self.rv['b']['distribution'][0])

        lea_s = float(self.rv['s']['distribution'][1])
        lea_p = float(self.rv['p']['distribution'][1])
        lea_k = float(self.rv['k']['distribution'][1])
        lea_g = float(self.rv['g']['distribution'][1])
        lea_b = float(self.rv['b']['distribution'][1])

        maj_s = float(self.rv['s']['distribution'][2])
        maj_p = float(self.rv['p']['distribution'][2])
        maj_k = float(self.rv['k']['distribution'][2])
        maj_g = float(self.rv['g']['distribution'][2])
        maj_b = float(self.rv['b']['distribution'][2])

        min_s = float(self.rv['s']['distribution'][3])
        min_p = float(self.rv['p']['distribution'][3])
        min_k = float(self.rv['k']['distribution'][3])
        min_g = float(self.rv['g']['distribution'][3])
        min_b = float(self.rv['b']['distribution'][3])

        cur = self.conn.cursor()

        #利用循环来使项目类型与项目分配参数匹配
        def initiator_sum():
            rv = []
            for x,y in [('S',ini_s),('P',ini_p),('K',ini_k),('G',ini_g),('B',ini_b)]:
                sql = '''SELECT SUM(SCORE * %s)
                         FROM REPORT
                         WHERE ININTIALOR = "%s"
                         AND PROJECT_SCORE_LEVEL = "%s";
                      ''' % (y,name,x)
                rv.append(cur.execute(sql).fetchone()[0])
            ini = sum([item for item in rv if item is not None])
            return ini

        def leader_sum():
            rv = []
            for x,y in [('S',lea_s),('P',lea_p),('K',lea_k),('G',lea_g),('B',lea_b)]:
                sql = '''SELECT SUM(SCORE * %s)
                         FROM REPORT
                         WHERE ININTIALOR = "%s"
                         AND PROJECT_SCORE_LEVEL = "%s"
                      ''' % (y,name,x)
                rv.append(cur.execute(sql).fetchone()[0])
            lea = sum([item for item in rv if item is not None])
            return lea

        # 注意,这里的查询语句只能用LIKE实现，因为所有人名字段是连在一起的，
        # 如果用 = ，在人名超过1位的情况下，只会得到None
        def major_sum():
            rv = []
            for x,y in [('S',maj_s),('P',maj_p),('K',maj_k),('G',maj_g),('B',maj_b)]:
                sql = '''SELECT SUM(SCORE * %s / MAJOR_PARTICIPATOR_COUNT)
                         FROM REPORT
                         WHERE MAJOR_PARTICIPATOR LIKE "%%%s%%"
                         AND PROJECT_SCORE_LEVEL = "%s";
                      ''' % (y,name,x)
                rv.append(cur.execute(sql).fetchone()[0])
            maj = sum([item for item in rv if item is not None])
            return maj

        def minor_sum():
            rv = []
            for x,y in [('S',min_s),('P',min_p),('K',min_k),('G',min_g),('B',min_b)]:
                sql = '''SELECT SUM(SCORE * %s / MINIOR_PARTICIPATOR_COUNT)
                         FROM REPORT
                         WHERE MINIOR_PARTICIPATOR LIKE "%%%s%%"
                         AND PROJECT_SCORE_LEVEL = "%s";
                      ''' % (y,name,x)
                rv.append(cur.execute(sql).fetchone()[0])
            min = sum([item for item in rv if item is not None])
            return min


        r = {'Initiator':round(initiator_sum(),1),
             'Leader':round(leader_sum(),1),
             'Major':round(major_sum(),1),
             'Minor':round(minor_sum(),1),
             'sum':round(initiator_sum()+leader_sum()+major_sum()+minor_sum(),1)
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