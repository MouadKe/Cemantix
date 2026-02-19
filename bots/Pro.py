import numpy as np
import random
from game_logic.services import WordSimilarityService
from game_logic.vector_db import VectorDB


class ProBot:
    def __init__(self, language='en'):
        self.language = language
        self.similarity_service = WordSimilarityService()
        self.vector_search = VectorDB()

    def get_next_guess(self, guesses):
        """
        guesses: List of dicts {"word": str, "similarity": float}
        Returns the bot's next guess as a string.
        """
        if len(guesses) < 2:
            return self._get_random_word()

        vectors = []
        scores = []
        for g in guesses:
            v = self.vector_search.get_word_vector(g["word"], self.language)
            if v is not None:
                vectors.append(v)
                scores.append(g["similarity"])

        if len(vectors) < 2:
            return self._get_random_word()

        best_guess = max(guesses, key=lambda x: x["similarity"])
        best_sim = best_guess["similarity"]
        best_word = best_guess["word"]
        
        # Strategy A: Early Game / Low Confidence (< 20%)
        # Random exploration around best or new random to escape bad starts.
        if best_sim < 20:
            if random.random() < 0.3:
                return self._get_random_word()
            
            v_best = self.vector_search.get_word_vector(best_word, self.language)
            if v_best is None: return self._get_random_word()
            
            noise = np.random.normal(0, 0.5, v_best.shape)
            target_vector = v_best + noise
            return self._get_unguessed_nearest(target_vector, guesses)

        # Strategy B: Hill Climbing (20 <= sim < 60)
        # Use Noob-like gradient (Best - SecondBest) for stability.
        if best_sim < 60:
            v_best = self.vector_search.get_word_vector(best_word, self.language)
            if v_best is None: return self._get_random_word()
            
            # Sticky: If last guess was best, explore its immediate neighborhood
            last_guess = guesses[-1]
            if last_guess['word'] == best_word:
                 return self._get_unguessed_nearest(v_best, guesses)
            
            # Gradient ascent if we have enough data
            if len(guesses) >= 2:
                sorted_local = sorted(guesses, key=lambda x: x["similarity"], reverse=True)
                v1 = self.vector_search.get_word_vector(sorted_local[1]["word"], self.language)
                
                if v1 is not None:
                     direction = v_best - v1
                     target = v_best + direction * 0.5
                     target /= np.linalg.norm(target)
                     return self._get_unguessed_nearest(target, guesses)
            
            return self._get_unguessed_nearest(v_best, guesses)

        # Strategy C: Extrapolation / Trend Projection (sim >= 60)
        # Direction = Best_Vector - Weighted_Average_Of_Other_Top_Guesses
        sorted_guesses = sorted(guesses, key=lambda x: x["similarity"], reverse=True)
        best_guess = sorted_guesses[0]
        v_best = self.vector_search.get_word_vector(best_guess["word"], self.language)
        if v_best is None: return self._get_random_word()
        
        rest_guesses = sorted_guesses[1:6] # Next 5 best
        if not rest_guesses:
             return self._get_unguessed_nearest(v_best, guesses)
             
        center_rest = np.zeros_like(v_best)
        total_weight = 0
        for g in rest_guesses:
             v = self.vector_search.get_word_vector(g["word"], self.language)
             if v is not None:
                 weight = (g["similarity"] / 100.0) ** 2
                 center_rest += v * weight
                 total_weight += weight
        
        if total_weight == 0:
             return self._get_unguessed_nearest(v_best, guesses)
             
        center_rest /= total_weight
        direction = v_best - center_rest
        
        norm_dir = np.linalg.norm(direction)
        if norm_dir > 0:
            direction /= norm_dir
            
        # Dynamic step size based on how close we are
        step_size = 0.5 * ((100 - best_guess["similarity"]) / 100.0)
        step_size = min(0.5, max(0.2, step_size))
        
        target_vector = v_best + (direction * step_size)
        target_vector = target_vector / np.linalg.norm(target_vector)
        
        return self._get_unguessed_nearest(target_vector, guesses)

    def _get_unguessed_nearest(self, guess_vector, guesses):
        """Find nearest neighbor not in guesses."""
        guessed_words = {g["word"].lower() for g in guesses}
        top_k = 5

        while True:
            nearest_words = self.vector_search.get_nearest_word(
                guess_vector, self.language, top_k=top_k
            )

            if not nearest_words:
                return self._get_random_word()

            for word in nearest_words:
                if word.lower() not in guessed_words:
                    return word

            top_k *= 2
            if top_k > 1000:
                return self._get_random_word()

    def _get_random_word(self):
        """Fallback: pick a random word from the vocabulary."""
        words = self.vector_search.get_word_list(self.language)
        if words:
            return random.choice(words)
        return "doctor"  # fallback
