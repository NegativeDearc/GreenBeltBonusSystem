# coding=utf-8
__author__ = 'SXChen'


# sqlite3 注册函数
def count_member(name):
    '''
    注册函数，以逗号分割，计算人名字段的个数。
    有潜在的问题，若最末以逗号+空格结尾，则计算数目+1
    已在模板中加入正则防止最末产生逗号+空格
    未来考虑使用正则匹配re.split('\s*,\s*',string)
    '''
    s = name.split(',')
    if s[-1] == '':
        return len(s)-1
    else:
        return len(s)