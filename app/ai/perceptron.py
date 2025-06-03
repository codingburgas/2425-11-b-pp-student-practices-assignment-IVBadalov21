import numpy as np
import joblib

class Perceptron:
    def __init__(self, input_size, num_classes, learning_rate=0.1):
        self.weights = np.zeros((num_classes, input_size))
        self.bias = np.zeros(num_classes)
        self.lr = learning_rate

    def predict(self, x):
        scores = np.dot(self.weights, x) + self.bias
        return np.argmax(scores)

    def train(self, X, y, epochs=10):
        for epoch in range(epochs):
            errors = 0
            for xi, yi in zip(X, y):
                pred = self.predict(xi)
                if pred != yi:
                    self.weights[yi] += self.lr * xi
                    self.weights[pred] -= self.lr * xi
                    self.bias[yi] += self.lr
                    self.bias[pred] -= self.lr
                    errors += 1
            print(f"Epoch {epoch + 1}, Errors: {errors}")

    def save(self, path):
        joblib.dump((self.weights, self.bias), path)

    def load(self, path):
        self.weights, self.bias = joblib.load(path)
