import unittest
from app.models.perceptron import Perceptron
import numpy as np

class TestPerceptron(unittest.TestCase):
    def test_training(self):
        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        y = np.array([0, 0, 0, 1])
        p = Perceptron(input_dim=2)
        p.train(X, y)
        self.assertEqual(p.predict([1, 1]), 1)
