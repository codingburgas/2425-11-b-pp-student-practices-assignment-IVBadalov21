import numpy as np
import re
from collections import Counter

TOP_CHARS = 30

class FeatureExtractor:
    def __init__(self):
        self.chars = []

    def fit(self, texts):
        all_text = ''.join(texts).lower()
        all_text = re.sub(r"[^a-z\u00e0-\u00ff]", "", all_text)
        counter = Counter(all_text)
        self.chars = [c for c, _ in counter.most_common(TOP_CHARS)]

    def transform(self, texts):
        result = []
        for text in texts:
            vec = [text.lower().count(c) for c in self.chars]
            total = max(1, sum(vec))
            result.append(np.array(vec) / total)
        return np.array(result)