# -*- coding:utf-8 -*-
__author__ = 'SXChen'

from sys import platform
import os
import json
import bisect


# 统一项目积分规则的接口
class ruleMaker(object):
    def __init__(self):
        if platform.startswith('win'):
            self.path = os.path.abspath(os.path.dirname(__file__)) + '\\config.json'
        else:
            self.path = os.path.abspath(os.path.dirname(__file__)) + '/config.json'

    def golden_score_rule(self):
        pass

    def project_score_rule(self):
        pass

    def project_distribution_rule(self):
        pass

    def rules_api_info(self):
        with open(self.path,'r') as f:
            return json.load(f)

    def update_config(self,data):
        '''更新本地json文件'''
        with open(self.path,'r') as f:
            origin_data = json.load(f)
        #
        origin_data.update(s1={'value':data['s_s']})
        origin_data.update(p1={'value':data['s_p']})
        origin_data.update(k1={'value':data['s_k']})
        origin_data.update(g1={'value':data['s_g1']})
        origin_data.update(g2={'value':data['s_g2']})
        origin_data.update(g3={'value':data['s_g3']})
        origin_data.update(b1={'value':data['s_b1']})
        #
        origin_data.update(s={'value':data['p_s'],
                              'distribution':[data['ini_s'],data['lea_s'],data['maj_s'],data['min_s']]})
        origin_data.update(p={'value':data['p_p'],
                              'distribution':[data['ini_p'],data['lea_p'],data['maj_p'],data['min_p']]})
        origin_data.update(k={'value':data['p_k'],
                              'distribution':[data['ini_k'],data['lea_k'],data['maj_k'],data['min_k']]})
        origin_data.update(g={'value':data['p_g'],
                              'distribution':[data['ini_g'],data['lea_g'],data['maj_g'],data['min_g']]})
        origin_data.update(b={'value':data['p_b'],
                              'distribution':[data['ini_b'],data['lea_b'],data['maj_b'],data['min_b']]})
        #
        origin_data.update(duplicability={"level1":data['duplicability_level_1'],
                                          "level2":data['duplicability_level_2'],
                                          "level3":data['duplicability_level_3']})
        origin_data.update(resource_usage={"level1":data['resource_usage_level_1'],
                                           "level2":data['resource_usage_level_2'],
                                           "level3":data['resource_usage_level_3']})
        origin_data.update(implement_period={"level1":data['implement_period_level_1'],
                                             "level2":data['implement_period_level_2'],
                                             "level3":data['implement_period_level_3']})
        origin_data.update(kpi_impact={"level1":data['kpi_level_1'],
                                       "level2":data['kpi_level_2'],
                                       "level3":data['kpi_level_3']})
        #
        origin_data.update(s1_range=data['s1_range'])
        origin_data.update(p1_range=data['p1_range'])
        origin_data.update(k1_range=data['k1_range'])
        origin_data.update(g1_range=data['g1_range'])
        origin_data.update(g2_range=data['g2_range'])
        origin_data.update(g3_range=data['g3_range'])
        origin_data.update(b_range=data['b_range'])

        origin_data.update(check_3=data['check_3'])
        origin_data.update(check_6=data['check_6'])

        with open(self.path,'w') as ff:
            json.dump(origin_data,ff)

    def golden_type_judging(self,data):
        range_data = ruleMaker.rules_api_info(self)
        data = float(data)
        # 积分规则调用,利用bisect 进行排序插值，若得1则居中,或者等于末端点
        if bisect.bisect(eval(range_data['s1_range']),data) == 1\
                or data == eval(range_data['s1_range'])[1]:
            return 's1'
        if bisect.bisect(eval(range_data['p1_range']),data) == 1\
                or data == eval(range_data['p1_range'])[1]:
            return 'p1'
        if bisect.bisect(eval(range_data['k1_range']),data) == 1\
                or data == eval(range_data['k1_range'])[1]:
            return 'k1'
        if bisect.bisect(eval(range_data['g1_range']),data) == 1\
                or data == eval(range_data['g1_range'])[1]:
            return 'g1'
        if bisect.bisect(eval(range_data['g2_range']),data) == 1\
                or data == eval(range_data['g2_range'])[1]:
            return 'g2'
        if bisect.bisect(eval(range_data['g3_range']),data) == 1\
                or data == eval(range_data['g3_range'])[1]:
            return 'g3'
        if bisect.bisect(eval(range_data['b_range']),data) == 1\
                or data == eval(range_data['b_range'])[1]:
            return 'b1'

if __name__ == '__main__':
    test = ruleMaker()
    # print test.path
    # print test.rules_api_info()['s']['value']
    # print test.rules_api_info()['k1']['value']
    # print test.rules_api_info()['b3']['value']
    # print type(test.rules_api_info()['b3']['value']) #unicode
    # print test.rules_api_info()['s']['distribution']
    # print test.rules_api_info()['s']['distribution'][3]
    # print type(test.rules_api_info()['s']['distribution']) #list
    print test.golden_type_judging(171)