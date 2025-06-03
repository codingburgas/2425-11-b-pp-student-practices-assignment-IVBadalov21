import pandas as pd
import numpy as np
from app.ai.perceptron import Perceptron
from app.ai.feature_extractor import FeatureExtractor
from sklearn.preprocessing import LabelEncoder
import joblib

DATA = [
    ("Hello, how are you?", "en"),
    ("I am very happy today!", "en"),
    ("Where is the station?", "en"),
    ("Nice to meet you!", "en"),
    ("What is your name?", "en"),

    ("Hola, ¿cómo estás?", "es"),
    ("Estoy muy bien, gracias.", "es"),
    ("¿Dónde está la estación?", "es"),
    ("Hace calor hoy.", "es"),
    ("Me gusta la música.", "es"),

    ("Je suis fatigué.", "fr"),
    ("Ceci est un exemple.", "fr"),
    ("Où est la bibliothèque?", "fr"),
    ("J'aime la programmation.", "fr"),
    ("Il fait beau aujourd'hui.", "fr")
]


# Създай DataFrame и запази като CSV
df = pd.DataFrame(DATA, columns=["text", "label"])
df.to_csv("lang_dataset.csv", index=False)

# Обработка
texts = df["text"].tolist()
labels = df["label"].tolist()

le = LabelEncoder()
y = le.fit_transform(labels)

fe = FeatureExtractor()
fe.fit(texts)
X = fe.transform(texts)

model = Perceptron(input_size=X.shape[1], num_classes=len(le.classes_))
model.train(X, y, epochs=10)

# Записване
joblib.dump(model, "language_model.pkl")
joblib.dump(fe, "feature_extractor.pkl")
joblib.dump(le, "label_encoder.pkl")

print("Моделът е обучен и запазен успешно!")
