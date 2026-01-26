import random


class GuessGame:
    def __init__(self):
        self.number = random.randint(1, 100)
    
    
    def check(self, value):
        if value < self.number:
            return "Trop petit"
        elif value > self.number:
            return "Trop grand"
        else:
            return "Bravo 🎉"