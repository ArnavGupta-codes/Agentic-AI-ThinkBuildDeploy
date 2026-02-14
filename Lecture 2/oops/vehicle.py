class Vehicle:

    def __init__(self, name, wheels):
        self.name = name
        self.wheels = wheels

    def drive(self):
        print(f"{self.name} is driving...")