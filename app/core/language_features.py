import re
import unicodedata
import numpy as np
from collections import Counter
from typing import List, Dict, Set
import string

class LanguageFeatureExtractor:
    """
    Feature extractor for language detection supporting multiple languages
    including Unicode/Cyrillic support for Bulgarian
    """
    
    def __init__(self):
        """Initialize the feature extractor with language-specific patterns"""
        
        # Character n-gram sizes
        self.char_ngram_sizes = [1, 2, 3]
        
        # Language-specific character sets
        self.language_chars = {
            'en': set('abcdefghijklmnopqrstuvwxyz'),
            'es': set('abcdefghijklmnopqrstuvwxyzáéíóúüñ'),
            'fr': set('abcdefghijklmnopqrstuvwxyzàâäéèêëïîôöùûüÿç'),
            'de': set('abcdefghijklmnopqrstuvwxyzäöüß'),
            'bg': set('абвгдежзийклмнопрстуфхцчшщъьюя')
        }
        
        # Language-specific common patterns
        self.language_patterns = {
            'en': [r'\bthe\b', r'\band\b', r'\bof\b', r'\bto\b', r'\bin\b', r'\bis\b'],
            'es': [r'\bel\b', r'\bla\b', r'\bde\b', r'\by\b', r'\ben\b', r'\bque\b'],
            'fr': [r'\ble\b', r'\bde\b', r'\bet\b', r'\bà\b', r'\bun\b', r'\bce\b'],
            'de': [r'\bder\b', r'\bdie\b', r'\bdas\b', r'\bund\b', r'\bin\b', r'\bzu\b'],
            'bg': [r'\bи\b', r'\bна\b', r'\bв\b', r'\bе\b', r'\bза\b', r'\bсе\b']
        }
        
        # Common digrams and trigrams by language
        self.common_ngrams = {
            'en': ['th', 'he', 'in', 'er', 'an', 'ed', 'ing', 'ion', 'and'],
            'es': ['es', 'en', 'de', 'la', 'el', 'er', 'ar', 'ado', 'ion'],
            'fr': ['es', 'en', 'de', 'le', 'er', 'nt', 'tion', 'ent'],
            'de': ['en', 'er', 'ch', 'te', 'nd', 'st', 'ung', 'ich'],
            'bg': ['на', 'се', 'да', 'ат', 'то', 'ст', 'ен', 'та']
        }
        
        # Initialize feature names for consistent ordering
        self._initialize_feature_names()
    
    def _initialize_feature_names(self):
        """Initialize feature names for consistent feature vector ordering"""
        self.feature_names = []
        
        # Character frequency features
        all_chars = set()
        for chars in self.language_chars.values():
            all_chars.update(chars)
        
        for char in sorted(all_chars):
            self.feature_names.append(f'char_freq_{char}')
        
        # N-gram features
        for size in self.char_ngram_sizes:
            self.feature_names.append(f'avg_ngram_{size}_freq')
            self.feature_names.append(f'max_ngram_{size}_freq')
        
        # Language-specific pattern features
        for lang in ['en', 'es', 'fr', 'de', 'bg']:
            self.feature_names.append(f'lang_pattern_{lang}')
            self.feature_names.append(f'char_ratio_{lang}')
            self.feature_names.append(f'common_ngrams_{lang}')
        
        # Text statistics features
        self.feature_names.extend([
            'text_length',
            'avg_word_length',
            'vowel_ratio',
            'consonant_ratio',
            'digit_ratio',
            'punct_ratio',
            'uppercase_ratio',
            'whitespace_ratio',
            'unicode_ratio',
            'cyrillic_ratio',
            'latin_ratio'
        ])
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text while preserving Unicode characters"""
        # Convert to lowercase
        text = text.lower()
        
        # Normalize Unicode characters
        text = unicodedata.normalize('NFC', text)
        
        return text
    
    def _extract_char_frequencies(self, text: str) -> Dict[str, float]:
        """Extract character frequency features"""
        if not text:
            return {}
            
        char_counts = Counter(text)
        text_length = len(text)
        
        char_freqs = {}
        all_chars = set()
        for chars in self.language_chars.values():
            all_chars.update(chars)
        
        for char in all_chars:
            char_freqs[f'char_freq_{char}'] = char_counts.get(char, 0) / text_length
            
        return char_freqs
    
    def _extract_ngram_features(self, text: str) -> Dict[str, float]:
        """Extract n-gram based features"""
        features = {}
        
        for n in self.char_ngram_sizes:
            if len(text) < n:
                features[f'avg_ngram_{n}_freq'] = 0.0
                features[f'max_ngram_{n}_freq'] = 0.0
                continue
                
            ngrams = [text[i:i+n] for i in range(len(text) - n + 1)]
            ngram_counts = Counter(ngrams)
            
            if ngrams:
                freq_values = list(ngram_counts.values())
                features[f'avg_ngram_{n}_freq'] = np.mean(freq_values) / len(text)
                features[f'max_ngram_{n}_freq'] = max(freq_values) / len(text)
            else:
                features[f'avg_ngram_{n}_freq'] = 0.0
                features[f'max_ngram_{n}_freq'] = 0.0
                
        return features
    
    def _extract_language_specific_features(self, text: str) -> Dict[str, float]:
        """Extract language-specific pattern features"""
        features = {}
        
        for lang in ['en', 'es', 'fr', 'de', 'bg']:
            # Pattern matching features
            pattern_count = 0
            for pattern in self.language_patterns[lang]:
                pattern_count += len(re.findall(pattern, text, re.IGNORECASE))
            
            features[f'lang_pattern_{lang}'] = pattern_count / max(1, len(text.split()))
            
            # Character set ratio
            lang_chars = self.language_chars[lang]
            char_matches = sum(1 for char in text if char in lang_chars)
            features[f'char_ratio_{lang}'] = char_matches / max(1, len(text))
            
            # Common n-grams ratio
            common_ngram_count = 0
            for ngram in self.common_ngrams[lang]:
                common_ngram_count += text.count(ngram)
            
            features[f'common_ngrams_{lang}'] = common_ngram_count / max(1, len(text))
        
        return features
    
    def _extract_text_statistics(self, text: str) -> Dict[str, float]:
        """Extract general text statistics"""
        if not text:
            return {name: 0.0 for name in self.feature_names if name.startswith(('text_', 'avg_', 'vowel_', 'consonant_', 'digit_', 'punct_', 'uppercase_', 'whitespace_', 'unicode_', 'cyrillic_', 'latin_'))}
        
        features = {}
        text_len = len(text)
        
        # Basic text statistics
        features['text_length'] = text_len
        
        # Word length statistics
        words = text.split()
        if words:
            features['avg_word_length'] = np.mean([len(word) for word in words])
        else:
            features['avg_word_length'] = 0.0
        
        # Character type ratios
        vowels = 'aeiouаеиоуыэюя'
        consonants = 'bcdfghjklmnpqrstvwxyzбвгджзйклмнпрстфхцчшщъь'
        
        vowel_count = sum(1 for char in text.lower() if char in vowels)
        consonant_count = sum(1 for char in text.lower() if char in consonants)
        digit_count = sum(1 for char in text if char.isdigit())
        punct_count = sum(1 for char in text if char in string.punctuation)
        upper_count = sum(1 for char in text if char.isupper())
        space_count = sum(1 for char in text if char.isspace())
        
        features['vowel_ratio'] = vowel_count / text_len
        features['consonant_ratio'] = consonant_count / text_len
        features['digit_ratio'] = digit_count / text_len
        features['punct_ratio'] = punct_count / text_len
        features['uppercase_ratio'] = upper_count / text_len
        features['whitespace_ratio'] = space_count / text_len
        
        # Unicode character analysis
        ascii_count = sum(1 for char in text if ord(char) < 128)
        cyrillic_count = sum(1 for char in text if '\u0400' <= char <= '\u04ff')
        latin_count = sum(1 for char in text if char.isalpha() and ord(char) < 256)
        
        features['unicode_ratio'] = (text_len - ascii_count) / text_len
        features['cyrillic_ratio'] = cyrillic_count / text_len
        features['latin_ratio'] = latin_count / text_len
        
        return features
    
    def extract_features(self, text: str) -> np.ndarray:
        """
        Extract all features from text and return as numpy array
        
        Args:
            text: Input text to extract features from
            
        Returns:
            Feature vector as numpy array
        """
        if not text or not text.strip():
            return np.zeros(len(self.feature_names))
        
        # Normalize text
        normalized_text = self._normalize_text(text)
        
        # Extract different types of features
        features = {}
        
        # Character frequencies
        features.update(self._extract_char_frequencies(normalized_text))
        
        # N-gram features
        features.update(self._extract_ngram_features(normalized_text))
        
        # Language-specific features
        features.update(self._extract_language_specific_features(normalized_text))
        
        # Text statistics
        features.update(self._extract_text_statistics(normalized_text))
        
        # Convert to ordered feature vector
        feature_vector = []
        for feature_name in self.feature_names:
            feature_vector.append(features.get(feature_name, 0.0))
        
        return np.array(feature_vector, dtype=np.float32)
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names in order"""
        return self.feature_names.copy()
    
    def get_info(self) -> Dict[str, any]:
        """Get information about the feature extractor"""
        return {
            'feature_count': len(self.feature_names),
            'supported_languages': list(self.language_chars.keys()),
            'ngram_sizes': self.char_ngram_sizes,
            'unicode_support': True,
            'cyrillic_support': True
        }
import re
import numpy as np
from typing import List, Dict, Any
import unicodedata

class LanguageFeatureExtractor:
    """
    Feature extractor for language detection
    Extracts linguistic features from text samples
    """
    
    def __init__(self):
        """Initialize the feature extractor"""
        self.feature_names = [
            'avg_word_length', 'vowel_ratio', 'consonant_ratio',
            'cyrillic_ratio', 'latin_ratio', 'space_ratio',
            'punctuation_ratio', 'digit_ratio', 'uppercase_ratio',
            'sentence_count', 'word_count', 'char_frequency_en',
            'char_frequency_es', 'char_frequency_fr', 'char_frequency_bg',
            'char_frequency_de', 'trigram_features'
        ]
        
        # Language-specific character patterns
        self.language_chars = {
            'en': set('abcdefghijklmnopqrstuvwxyz'),
            'es': set('abcdefghijklmnopqrstuvwxyzñáéíóúü'),
            'fr': set('abcdefghijklmnopqrstuvwxyzàâäçéèêëïîôöùûüÿ'),
            'bg': set('абвгдежзийклмнопрстуфхцчшщъьюя'),
            'de': set('abcdefghijklmnopqrstuvwxyzäöüß')
        }
    
    def extract_features(self, text: str) -> np.ndarray:
        """
        Extract features from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Feature vector as numpy array
        """
        if not text:
            return np.zeros(len(self.feature_names))
        
        text = text.lower()
        features = []
        
        # Basic text statistics
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / max(word_count, 1)
        features.append(avg_word_length)
        
        # Character type ratios
        vowels = 'aeiouаеиоуыэюя'
        vowel_count = sum(1 for char in text if char in vowels)
        features.append(vowel_count / max(char_count, 1))  # vowel_ratio
        
        consonants = 'bcdfghjklmnpqrstvwxyzбвгджзклмнпрстфхцчшщ'
        consonant_count = sum(1 for char in text if char in consonants)
        features.append(consonant_count / max(char_count, 1))  # consonant_ratio
        
        # Script ratios
        cyrillic_count = sum(1 for char in text if '\u0400' <= char <= '\u04FF')
        features.append(cyrillic_count / max(char_count, 1))  # cyrillic_ratio
        
        latin_count = sum(1 for char in text if 'a' <= char <= 'z' or 'A' <= char <= 'Z')
        features.append(latin_count / max(char_count, 1))  # latin_ratio
        
        # Other ratios
        space_count = text.count(' ')
        features.append(space_count / max(char_count, 1))  # space_ratio
        
        punct_count = sum(1 for char in text if char in '.,!?;:()[]{}"-')
        features.append(punct_count / max(char_count, 1))  # punctuation_ratio
        
        digit_count = sum(1 for char in text if char.isdigit())
        features.append(digit_count / max(char_count, 1))  # digit_ratio
        
        upper_count = sum(1 for char in text if char.isupper())
        features.append(upper_count / max(char_count, 1))  # uppercase_ratio
        
        # Sentence and word counts (normalized)
        sentence_count = len(re.split(r'[.!?]+', text))
        features.append(sentence_count / max(char_count, 1))  # sentence_count
        features.append(word_count / max(char_count, 1))  # word_count
        
        # Language-specific character frequencies
        for lang in ['en', 'es', 'fr', 'bg', 'de']:
            lang_chars = self.language_chars[lang]
            lang_char_count = sum(1 for char in text if char in lang_chars)
            features.append(lang_char_count / max(char_count, 1))
        
        # Simple trigram features (average)
        trigrams = [text[i:i+3] for i in range(len(text)-2)]
        trigram_score = len(set(trigrams)) / max(len(trigrams), 1)
        features.append(trigram_score)
        
        return np.array(features, dtype=np.float32)
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        return self.feature_names.copy()
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the feature extractor"""
        return {
            'feature_count': len(self.feature_names),
            'supported_languages': list(self.language_chars.keys()),
            'unicode_support': True,
            'cyrillic_support': True
        }
