import cPickle as pickle
class Person:  
    def __init__(self,n,a):  
        self.name=n  
        self.age=a  
    def show(self):  
        print self.name+"_"+str(self.age)  
aa = Person("JGood", 2)  
aa.show()  
f=open('test.txt','w')
pickle.dump(aa,f,0)  
f.close()  
#del Person  
f=open('test.txt','r')
bb=pickle.load(f)  
f.close()  
bb.show()

cc = pickle.dumps(aa)
print(cc)
dd = pickle.loads(cc)
dd.show()