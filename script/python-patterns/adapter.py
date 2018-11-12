class Dog(object):
    def __init__(self):
        self.name = 'Dog'

    def bark(self):
        return "woof!"

class Cat(object):
    def __init__(self):
        self.name = 'Cat'

    def meow(self):
        return "miao!"

class Human(object):
    def __init__(self):
        self.name = 'liliang'

    def speak(self):
        return 'hello!'

class Car(object):
    def __init__(self):
        self.name = 'car'

    def make_noise(self):
        return 'vroom!'

class Adapter(object):
    def __init__(self, obj, **adapted_method):
        self.obj = obj
        self.__dict__.update(adapted_method)

    def __getattr__(self, item):
        return getattr(self.obj, item)

    def original_dict(self):
        return self.obj.__dict__

dog = Dog()
cat = Cat()
man = Human()
car = Car()

objects = []
objects.append(Adapter(dog, say=dog.bark))
objects.append(Adapter(cat, say=cat.meow))
objects.append(Adapter(man, say=man.speak))
objects.append(Adapter(car, say=car.make_noise))

[print(a.say(), a.name) for a in objects if hasattr(a, 'say')]

