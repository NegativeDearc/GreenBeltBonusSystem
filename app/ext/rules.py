# -*- coding:utf-8 -*-
__author__ = 'SXChen'

from sys import platform
import os
import json

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

        origin_data.update(s1={'value':data['s_s']})
        origin_data.update(p1={'value':data['s_p']})
        origin_data.update(k1={'value':data['s_k']})
        origin_data.update(g1={'value':data['s_g1']})
        origin_data.update(g2={'value':data['s_g2']})
        origin_data.update(g3={'value':data['s_g3']})
        origin_data.update(b1={'value':data['s_b1']})
        origin_data.update(b2={'value':data['s_b2']})
        origin_data.update(b3={'value':data['s_b3']})

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
        with open(self.path,'w') as ff:
            json.dump(origin_data,ff)

    def update_triggers(self,conn,data):
        '''更新数据库触发器'''
        trigger = '''DROP TRIGGER IF EXISTS [S];
                     DROP TRIGGER IF EXISTS [P];
                     DROP TRIGGER IF EXISTS [K];
                     DROP TRIGGER IF EXISTS [G1];
                     DROP TRIGGER IF EXISTS [G2];
                     DROP TRIGGER IF EXISTS [G3];
                     DROP TRIGGER IF EXISTS [B1];
                     DROP TRIGGER IF EXISTS [B2];
                     DROP TRIGGER IF EXISTS [B3];
                     DROP TRIGGER IF EXISTS [P_S];
                     DROP TRIGGER IF EXISTS [P_P];
                     DROP TRIGGER IF EXISTS [P_K];
                     DROP TRIGGER IF EXISTS [P_G];
                     DROP TRIGGER IF EXISTS [P_B];
                     DROP TRIGGER IF EXISTS [ACTIVE];

                    CREATE TRIGGER [S]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = %s
                    WHERE GOLDEN_IDEA_LEVEL = "S1";
                    END;

                    CREATE TRIGGER [P]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = %s
                    WHERE GOLDEN_IDEA_LEVEL = "P1";
                    END;

                    CREATE TRIGGER [K]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = %s
                    WHERE GOLDEN_IDEA_LEVEL = "K1";
                    END;

                    CREATE TRIGGER [G1]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = %s
                    WHERE GOLDEN_IDEA_LEVEL = "G1";
                    END;

                    CREATE TRIGGER [G2]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = %s
                    WHERE GOLDEN_IDEA_LEVEL = "G2";
                    END;

                    CREATE TRIGGER [G3]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = %s
                    WHERE GOLDEN_IDEA_LEVEL = "G3";
                    END;

                    CREATE TRIGGER [B1]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = %s
                    WHERE GOLDEN_IDEA_LEVEL = "B1";
                    END;

                    CREATE TRIGGER [B2]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = %s
                    WHERE GOLDEN_IDEA_LEVEL = "B2";
                    END;

                    CREATE TRIGGER [B3]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = %s
                    WHERE GOLDEN_IDEA_LEVEL = "B3";
                    END;

                    CREATE TRIGGER [P_S]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET PROJECT_SCORE = %s
                    WHERE PROJECT_SCORE_LEVEL = "S";
                    END;

                    CREATE TRIGGER [P_P]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET PROJECT_SCORE = %s
                    WHERE PROJECT_SCORE_LEVEL = "P";
                    END;

                    CREATE TRIGGER [P_K]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET PROJECT_SCORE = %s
                    WHERE PROJECT_SCORE_LEVEL = "K";
                    END;

                    CREATE TRIGGER [P_G]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET PROJECT_SCORE = %s
                    WHERE PROJECT_SCORE_LEVEL = "G";
                    END;

                    CREATE TRIGGER [P_B]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET PROJECT_SCORE = %s
                    WHERE PROJECT_SCORE_LEVEL = "B";
                    END;

                    CREATE TRIGGER [ACTIVE]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET ACTIVE_SCORE = %s
                    WHERE GOLDEN_IDEA_LEVEL = 'S1' ;

                    UPDATE [SCORE_CARD]
                    SET ACTIVE_SCORE = %s
                    WHERE GOLDEN_IDEA_LEVEL = 'P1' ;
                    END
        ''' % (data['s_s'],data['s_p'],data['s_k'],data['s_g1'],data['s_g2'],data['s_g3'],
               data['s_b1'],data['s_b2'],data['s_b3'],data['p_s'],data['p_p'],data['p_k'],
               data['p_g'],data['p_b'],data['s_s'],data['s_p'])

        #print trigger
        cur = conn.cursor()
        cur.executescript(trigger)
        conn.commit()

if __name__ == '__main__':
    test = ruleMaker()
    #print test.path
    print test.rules_api_info()['s']['value']
    print test.rules_api_info()['k1']['value']
    print test.rules_api_info()['b3']['value']
    print type(test.rules_api_info()['b3']['value']) #unicode
    print test.rules_api_info()['s']['distribution']
    print test.rules_api_info()['s']['distribution'][3]
    print type(test.rules_api_info()['s']['distribution']) #list