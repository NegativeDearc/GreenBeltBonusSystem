#-*- coding:utf-8 -*-

class newDict(dict):
   '''从原始类dict继承，加入add方法来实现字典的加法'''
   def __add__(self,y):
       # initial an empty dic
       rv = newDict()
       # 类型检查 自动使其符合新式类
       if not isinstance(y,dict):
           raise TypeError("Type didn't match")
       else:
           y = newDict(y)
       # search same keys,add them
       for key in dict.keys(self):
           if y.has_key(key):
               rv[key] = self.get(key)+y.get(key)
           else:
               rv[key] = self.get(key)
       return rv

if __name__ == '__main__':
    a = newDict(a=1,b=3)
    b = dict(a=4,b=5)
    c = dict(c=6,a=7,b=8)
    print a+b # {'a':5,'b':8}
    print a+c
    # 注意dict没有__add__方法，
    # 所以字典不能直接加上新式字典
    print b+a # 出错