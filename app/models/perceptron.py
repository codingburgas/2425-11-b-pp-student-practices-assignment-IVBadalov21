import numpy as np

class Perceptron:
    def __init__(self, input_dim, learning_rate=0.1, epochs=1000):
        self.weights = np.zeros(input_dim)
        self.bias = 0
        self.lr = learning_rate
        self.epochs = epochs

    def activation(self, x):
        return 1 if x >= 0 else 0

    def predict(self, X):
        linear_output = np.dot(X, self.weights) + self.bias
        return self.activation(linear_output)

    def train(self, X, y):
        for _ in range(self.epochs):
            for xi, target in zip(X, y):
                pred = self.predict(xi)
                update = self.lr * (target - pred)
                self.weights += update * xi
                self.bias += update
