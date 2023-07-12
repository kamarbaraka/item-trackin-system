class Test:

    name = "kamar"
    age = 23

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Test, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.count = 1

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def getAge(self):
        return self.age

    def setAge(self, age):
        self.age = age

if __name__ == '__main__':
    test = Test()
    test1 = Test()

    test1.setName("baraka")
    print(test.getName())
    print(test1.getName())
