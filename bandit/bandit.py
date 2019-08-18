import numpy as np

class Bandit:
    def __init__(self, mean: float = 0):
        self.mean = mean
        self.N = 0

    def update(self, x):
        self.N += 1
        self.mean = (1 - 1.0 / self.N) * self.mean + (1.0 / self.N) * x
