# -*- coding:utf-8 -*-
__author__ = 'SXChen'

from werkzeug.security import generate_password_hash, check_password_hash
from config import config

class passwordSecurity(object):
    '''generate_password_hash 加盐密码, check_password_hash 返回比较值 True/False'''

    def __init__(self, conn):
        self.conn = conn
        self.path = config['production'].DATABASE_PATH

    def verify_hash_password(self,user,pwd):
        cur = self.conn.cursor()
        sql_pwd_hash = '''SELECT PASSWORD
                          FROM USER_PASSWORD
                          WHERE USER = "%s"''' % user

        # 注意！若未查询到，返回None,None 是不可以参加运算的
        pwd_hash = cur.execute(sql_pwd_hash).fetchone()

        if pwd_hash is not None:
            rv = pwd_hash[0]
        else:
            rv = ''
        return check_password_hash(rv,pwd)

    def generate_hash_password(self, pwd):
        '''sqlite3 注册函数,对大小写敏感'''
        rv = generate_password_hash(pwd,salt_length=16)
        return rv

    def register_user(self):
        '''注册用户，并hash密码'''
        pass

    def change_password(self):
        pass

if __name__ == '__main__':
    test = passwordSecurity('conn')
    test.generate_hash_password('070662')
    test.generate_hash_password('124464')
    print test.path
