from vehicle import Vehicle

class Car(Vehicle):

    def __init__(self, make, model, year, colour):
        self.make = make
        self.model = model
        self.name = make + model
        self.wheels = 4
        self.year = year
        self.colour = colour
        super().__init__(self.name, self.wheels)

    def drift(self):
        print(f"{self.name} has drifted.")