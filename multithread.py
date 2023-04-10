class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        
    def start(self):
        print(f"{self.make} {self.model} ({self.year}) is starting...")

my_car = Car("Honda", "Civic", 2021)
my_car.start() # Output: Honda Civic (2021) is starting...