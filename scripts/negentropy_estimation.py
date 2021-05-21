import numpy as np

def g(y):
    return np.log(np.cosh(y))

def negentropy(y):
    mean = np.mean(y)
    std = np.std(y)
    u = (y - mean) / std
    gaussian = np.random.normal(size=len(u))
    return np.square(np.mean(g(u)) - np.mean(g(gaussian)))
