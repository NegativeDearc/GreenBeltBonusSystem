# -*- coding:utf-8 -*-
__author__ = 'Dearc'

from rules import ruleMaker


class insert_records(object):
    '''模块作用：向数据库插入操作的动作、分值来作为日志，供后续调用
       依赖模块：rules，从中获取点子分和项目积分的分值信息
       注意事项：务必注意分值信息的类型是否为int/float
    '''

    def __init__(self):
        '''从rules中获取分值信息'''
        self.rul = ruleMaker()
        self.rv = self.rul.rules_api_info()

    def prj_launch(self, project_type=None, prj_num=None, conn=None, update=False):
        # 初始化游标
        cur = conn.cursor()
        # 查询语句
        total_score_sql = '''SELECT TOTAL_SCORE
                             FROM [SCORE_CARD]
                             WHERE PROJECT_NUMBER = "%s"''' % prj_num
        # 结果一般不为None
        total_score = cur.execute(total_score_sql).fetchone()[0]

        if project_type == 'S' or project_type == 'P':
            res = total_score
            # 关闭S/P类型节点检查
            close_check_point_1 = '''UPDATE [PROJECT_INFO]
                                     SET [3_MONTH_CHECK]=1,
                                       [6_MONTH_CHECK]=1
                                     WHERE [PROJECT_NUMBER] = "%s"''' % prj_num
            cur.execute(close_check_point_1)
            conn.commit()
        else:
            res = 0
            close_check_point_0 = '''UPDATE [PROJECT_INFO]
                                     SET [3_MONTH_CHECK]=0,
                                         [6_MONTH_CHECK]=0
                                     WHERE [PROJECT_NUMBER] = "%s"''' % prj_num
            cur.execute(close_check_point_0)
            conn.commit()

        insert_records = '''INSERT INTO MONTHLY_ACTION
                            (PROJECT_NUM,DATE,ACTION,SCORE)
                            VALUES ("%s",DATE('now'),"%s","%s");
                         ''' % (prj_num, 'project launched', res)

        # 在比较运算中is的速度要比==快,
        # 当update=True时,更新MONTHLY_ACTION表中project launched的分值
        if update is True:
            insert_records = '''UPDATE MONTHLY_ACTION
                                SET SCORE=%s
                                WHERE PROJECT_NUM="%s"
                                AND ACTION="project launched";''' % (res,prj_num)

        cur.execute(insert_records)
        conn.commit()

    def insert_release_detail(self, conn, prj_num, flag={1, 2, 3, 4}):
        '''
        flag = 1 ->3 month release
        flag = 2 ->6 month release
        flag = 3 ->3 month closed
        flag = 4 ->6 month closed
        '''
        # 查询点子分数和项目分数
        tmp = '''SELECT TOTAL_SCORE,PROJECT_SCORE_LEVEL
                 FROM SCORE_CARD
                 WHERE PROJECT_NUMBER = "%s"''' % prj_num
        # 游标
        cur = conn.cursor()
        # 解包
        total_score,pj_type = cur.execute(tmp).fetchall()[0]
        # 需根据配置决定每个检查点释放的比例
        flag_description = None
        total = None
        # 3个月释放
        if flag == 1:
            # S/P 类型的规则
            if pj_type == 'S' or pj_type == 'P':
                flag_description = 'S/P 3 month release'
                total = int(total_score)
            # 非S/P类型的规则
            else:
                flag_description = '3 month release'
                total = int(total_score * float(self.rv['check_3']))
        # 6个月释放
        if flag == 2:
            flag_description = '6 month release'
            total = int(total_score * float(self.rv['check_6']))
        # 3个月未通过关闭，不得分
        if flag == 3:
            flag_description = '3 month closed'
            total = 0
        # 6个月未通过关闭，不得分
        if flag == 4:
            flag_description = '6 month closed'
            total = 0

        # 如何将flag从数值转为说明
        insert_records = '''INSERT INTO MONTHLY_ACTION
                            (PROJECT_NUM,DATE,ACTION,SCORE)
                            VALUES ("%s",DATE('now'),"%s","%s");
                         ''' % (prj_num, flag_description, total)
        cur.execute(insert_records)
        conn.commit()
