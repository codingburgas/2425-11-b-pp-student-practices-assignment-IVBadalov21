import pickle
from app.core.perceptron import MultiClassPerceptron

def test_model():
    print("Loading trained model...")
    with open('app/data/model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    test_texts = {
        'en': "This is a test message in English. The model should detect this correctly.",
        'es': "Este es un mensaje de prueba en español. El modelo debería detectarlo correctamente.",
        'fr': "Ceci est un message test en français. Le modèle devrait le détecter correctement.",
        'bg': "Това е тестово съобщение на български. Моделът трябва да го открие правилно.",
        'de': "Dies ist eine Testnachricht auf Deutsch. Das Modell sollte dies korrekt erkennen."
    }
    
    print("\nTesting model predictions:")
    print("-" * 50)
    
    for true_lang, text in test_texts.items():
        prediction = model.predict(text)
        probabilities = model.predict_proba(text)
        
        print(f"\nTrue language: {true_lang}")
        print(f"Predicted: {prediction}")
        print("Probabilities:")
        for lang, prob in sorted(probabilities.items(), key=lambda x: x[1], reverse=True):
            print(f"  {lang}: {prob:.4f}")
        print("-" * 50)

if __name__ == '__main__':
    test_model() 