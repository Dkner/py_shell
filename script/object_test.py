class A(object):
    def __init__(self, name):
        self.id = 1
        self.name = name
        print('A names {}'.format(name))

    def foo(self):
        print('foo')

class B(A):
    def __init__(self):
        super().__init__(name='b')

    def bar(self):
        print('bar')

b = B()
b.foo()
b.bar()
print(b.id)