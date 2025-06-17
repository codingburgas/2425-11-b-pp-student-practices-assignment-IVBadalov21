import os
import pickle
import numpy as np
from app.core.perceptron import MultiClassPerceptron

def create_training_data():
    """Create some basic training data for each language"""
    training_data = {
        'en': [
            "Hello, how are you today?",
            "The quick brown fox jumps over the lazy dog.",
            "Python is a popular programming language.",
            "Machine learning is transforming technology.",
            "Welcome to our language detection system.",
            "This is a test message in English.",
            "The weather is beautiful today.",
            "I love programming and artificial intelligence.",
            "The internet has revolutionized communication.",
            "Data science is an exciting field."
        ],
        'es': [
            "Hola, ¿cómo estás hoy?",
            "El rápido zorro marrón salta sobre el perro perezoso.",
            "Python es un lenguaje de programación popular.",
            "El aprendizaje automático está transformando la tecnología.",
            "Bienvenido a nuestro sistema de detección de idiomas.",
            "Este es un mensaje de prueba en español.",
            "El clima está hermoso hoy.",
            "Me encanta programar e inteligencia artificial.",
            "Internet ha revolucionado la comunicación.",
            "La ciencia de datos es un campo emocionante."
        ],
        'fr': [
            "Bonjour, comment allez-vous aujourd'hui?",
            "Le rapide renard brun saute par-dessus le chien paresseux.",
            "Python est un langage de programmation populaire.",
            "L'apprentissage automatique transforme la technologie.",
            "Bienvenue dans notre système de détection de langue.",
            "Ceci est un message test en français.",
            "Le temps est magnifique aujourd'hui.",
            "J'aime la programmation et l'intelligence artificielle.",
            "Internet a révolutionné la communication.",
            "La science des données est un domaine passionnant."
        ],
        'bg': [
            "Здравейте, как сте днес?",
            "Бързата кафява лисица прескача над мързеливото куче.",
            "Python е популярен език за програмиране.",
            "Машинното обучение трансформира технологията.",
            "Добре дошли в нашата система за откриване на език.",
            "Това е тестово съобщение на български.",
            "Времето е прекрасно днес.",
            "Обичам програмирането и изкуствения интелект.",
            "Интернет революционизира комуникацията.",
            "Науката за данните е вълнуваща област."
        ],
        'de': [
            "Hallo, wie geht es Ihnen heute?",
            "Der schnelle braune Fuchs springt über den faulen Hund.",
            "Python ist eine beliebte Programmiersprache.",
            "Maschinelles Lernen verändert die Technologie.",
            "Willkommen in unserem Spracherkennungssystem.",
            "Dies ist eine Testnachricht auf Deutsch.",
            "Das Wetter ist heute wunderschön.",
            "Ich liebe Programmierung und künstliche Intelligenz.",
            "Das Internet hat die Kommunikation revolutioniert.",
            "Datenwissenschaft ist ein spannendes Feld.",
            "Guten Morgen! Wie war dein Wochenende?",
            "Könnten Sie mir bitte helfen?",
            "Ich spreche nur ein wenig Deutsch.",
            "Straßenbahnfahren macht Spaß.",
            "Möchten Sie einen Kaffee trinken?",
            "Das ist überhaupt kein Problem.",
            "Übermorgen wird das Wetter besser.",
            "Fußball ist in Deutschland sehr beliebt.",
            "Ich habe meine Schlüssel verloren.",
            "Entschuldigung, wo ist die nächste Apotheke?",
            "Die Prüfung war ziemlich schwierig.",
            "Können Sie das bitte wiederholen?",
            "Ich verstehe das nicht.",
            "Herzlichen Glückwunsch zum Geburtstag!",
            "Das ist eine ausgezeichnete Idee."
        ]
    }
    return training_data

def train_and_save_model():
    """Train the model and save it to a file"""
    print("Training language detection model...")
    
    # Create model instance with faster training parameters
    model = MultiClassPerceptron(
        languages=['en', 'es', 'fr', 'bg', 'de'],
        learning_rate=0.1,  # Increased learning rate
        max_epochs=100,     # Reduced epochs
        tolerance=1e-3      # Increased tolerance for faster convergence
    )
    
    # Get training data
    training_data = create_training_data()
    
    # Prepare training data
    X = []
    y = []
    for lang, texts in training_data.items():
        for text in texts:
            X.append(text)
            y.append(lang)
    
    # Train the model
    metrics = model.train(X, y)
    print("\nTraining metrics:")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Loss: {metrics['loss']:.4f}")
    print(f"Training time: {metrics['training_time']:.2f} seconds")
    
    # Create data directory if it doesn't exist
    os.makedirs('app/data', exist_ok=True)
    
    # Save the model
    model_path = os.path.join('app', 'data', 'model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\nModel trained and saved to {model_path}")
    print("Training complete!")

if __name__ == '__main__':
    train_and_save_model() 