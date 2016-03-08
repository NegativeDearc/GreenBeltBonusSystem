class newDict(dict):
   def __add__(self,y):
       '''doc here'''

       # initial an empty dic
       rv = newDict()

       # type check
       if not isinstance(y,dict):
           raise TypeError("Type didn't match")

       # search same keys,add them
       for key in dict.keys(self):
           if y.has_key(key):
               rv[key] = self.get(key)+y.get(key)
           else:
               rv[key] = self.get(key)
       return rv
                
