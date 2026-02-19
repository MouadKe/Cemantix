import os
import csv
import numpy as np

class VectorDB:
    _instance = None
    _vectors = {}
    _words = {}
    _matrix = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorDB, cls).__new__(cls)
        return cls._instance

    def load_data(self, language='en'):
        if language in self._vectors:
            return

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_name = "mixed.csv"
        
        if language == 'fr':
             folder = "packs_fr"
        elif language == 'ar':
             folder = "packs_ar"
        else:
             folder = "packs"

        csv_path = os.path.join(base_path, "word_list", folder, file_name)

        if not os.path.exists(csv_path):
            print(f"VectorDB Error: Embedding file not found at {csv_path}")
            return

        print(f"Loading embeddings from {csv_path}...")
        vectors = {}
        words_list = []
        matrix_list = []

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 2:
                        continue
                    word = row[0].strip().lower()
                    try:
                        vec = np.array([float(x) for x in row[1:]], dtype=np.float32)
                        # Normalize vector
                        norm = np.linalg.norm(vec)
                        if norm > 0:
                            vec = vec / norm
                        
                        vectors[word] = vec
                        words_list.append(word)
                        matrix_list.append(vec)
                    except ValueError:
                        continue
            
            self._vectors[language] = vectors
            self._words[language] = words_list
            self._matrix[language] = np.array(matrix_list)
            print(f"Loaded {len(vectors)} words for {language} (Normalized).")
            
        except Exception as e:
            print(f"Error loading embeddings: {e}")

    def get_word_vector(self, word, language='en'):
        if language not in self._vectors:
            self.load_data(language)
        return self._vectors.get(language, {}).get(word.lower())

    def get_word_list(self, language='en'):
        if language not in self._words:
            self.load_data(language)
        return self._words.get(language, [])

    def get_nearest_word(self, vector, language='en', top_k=10):
        if language not in self._matrix:
            self.load_data(language)
        
        matrix = self._matrix.get(language)
        words = self._words.get(language)
        
        if matrix is None or len(matrix) == 0:
            return []

        # Normalize input vector if needed
        norm_v = np.linalg.norm(vector)
        if norm_v == 0:
            return []
        
        if abs(norm_v - 1.0) > 1e-6:
            vector = vector / norm_v
        
        # Calculate cosine similarity
        cosine_sims = np.dot(matrix, vector)
        
        # Get indices of top_k
        top_indices = np.argsort(cosine_sims)[-top_k:][::-1]
        
        return [words[i] for i in top_indices]

    def get_pack_words(self, pack_name, language='en'):
        """Loads words from a specific pack text file."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if language == 'fr':
             folder = "packs_fr"
        elif language == 'ar':
             folder = "packs_ar"
        else:
             folder = "packs"
             
        file_path = os.path.join(base_path, "word_list", folder, f"{pack_name}.txt")
        
        if not os.path.exists(file_path):
            return []
            
        words = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                words = [line.strip().lower() for line in f if line.strip()]
        except Exception:
            pass
        return words
