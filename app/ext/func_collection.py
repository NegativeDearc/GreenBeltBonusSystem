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

# sqlite3 注册函数
def golden_score(golden_type):
    '''根据输入的项目/金点子的类型，在配置表中找到分值信息
       插入数据库
    '''
    # 初始化项目配置信息表
    from rules import ruleMaker
    rul = ruleMaker()
    rv = rul.rules_api_info()
    # 根据类型，读取配置
    g = rv[str.lower(golden_type)]['value']
    return int(g)

# sqlite3 注册函数
def project_score(project_type):
    '''根据输入的项目/金点子的类型，在配置表中找到分值信息
       插入数据库
    '''
    # 初始化项目配置信息表
    from rules import ruleMaker
    rul = ruleMaker()
    rv = rul.rules_api_info()
    # 根据类型，读取配置
    # 注意project_type来自request.form,其类型为unicode
    p = rv[project_type.lower()]['value']
    return int(p)

def active_score_launched(golden_type,project_type,target_score):
    '''根据项目类型决定初始发放的分值
       S/P全部释放分值
       K/G/B类型初始不发放'''
    from rules import ruleMaker
    rul = ruleMaker()
    rv = rul.rules_api_info()
    # 读取金点子类型的分值
    g = int(rv[str.lower(golden_type)]['value'])
    # 读取项目积分
    p = int(rv[project_type.lower()]['value'])
    # S/P 类型直接激活所有积分=金点子+项目分+定向
    if project_type == 'S' or project_type == 'P':
        return g + p + int(target_score)
    else:
        return 0

if __name__ == '__main__':
    print project_score(u'P') # error can't use str in unicode
    print golden_score('s1')