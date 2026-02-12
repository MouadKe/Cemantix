import numpy as np
from sentence_transformers import SentenceTransformer
import os

class WordSimilarityService:
    _instance = None
    _models = {}
    _model_names = {
        'en': 'all-MiniLM-L6-v2',
        # 'fr': 'dangvantuan/sentence-camembert-base', # Good but 400MB+
        # 'ar': 'Omartificial-Intelligence-Space/Arabic-MiniLM-L12-v2-all-nli-triplet' # Good but ~400MB?
        # Let's use smaller ones if possible, but for now these are standard "specific" ones.
        'fr': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
        'ar': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WordSimilarityService, cls).__new__(cls)
        return cls._instance

    def load_model(self, language):
        if language not in self._models:
            model_name = self._model_names.get(language, self._model_names['en'])
            try:
                print(f"Loading {language} model: {model_name}...")
                self._models[language] = SentenceTransformer(model_name)
                print(f"Model for {language} loaded.")
            except Exception as e:
                print(f"Error loading model for {language}: {e}")
                return None
        return self._models[language]

    def compute_similarity(self, word1, word2, language='en'):
        model = self.load_model(language)
        if not model:
            return 0.0
        
        embeddings = model.encode([word1, word2])
        # Cosine similarity
        similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
        return float(similarity)

    def get_similarity_to_goal(self, guess_word, goal_word, language='en'):
        return self.compute_similarity(guess_word, goal_word, language)
