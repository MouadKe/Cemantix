import numpy as np
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_logic.services import WordSimilarityService


class ProBot:
    def __init__(self, language='en'):
        self.language = language
        self.similarity_service = WordSimilarityService()
        self.vector_search = IMAN_REPLACE()

    def get_next_guess(self, guesses):
        """
        guesses: List of dicts {"word": str, "similarity": float}
        Returns the bot's next guess as a string.
        """
        # Step 1: Not enough data → random guess
        if len(guesses) < 2:
            return self._get_random_word()

        # Step 2: Convert words → vectors
        vectors = []
        scores = []
        for g in guesses:
            v = self.vector_search.get_word_vector(g["word"], self.language)
            if v is not None:
                vectors.append(v)
                scores.append(g["similarity"])

        if len(vectors) < 2:
            return self._get_random_word()

        # Step 3: Compute weighted target estimate using all guesses
        target_estimate = np.zeros_like(vectors[0])
        for v, s in zip(vectors, scores):
            weight = (s / 100.0) ** 3
            target_estimate += v * weight

        norm = np.linalg.norm(target_estimate)
        if norm == 0:
            return self._get_random_word()
        target_estimate /= norm

        # Step 4: Select best current guess
        best_guess = max(guesses, key=lambda x: x["similarity"])
        v_best = self.vector_search.get_word_vector(best_guess["word"], self.language)

        if v_best is None:
            return self._get_random_word()

        # Step 5: Compute direction toward estimate
        direction = target_estimate - v_best

        # Step 6: Adaptive step size — smaller when we're already close
        step_size = (100 - best_guess["similarity"]) / 100

        # Step 7: Generate next guess vector
        guess_vector = v_best + step_size * direction
        norm = np.linalg.norm(guess_vector)
        if norm == 0:
            return self._get_random_word()
        guess_vector /= norm

        # Step 8: Find nearest word, skipping already guessed words
        return self._get_unguessed_nearest(guess_vector, guesses)

    def _get_unguessed_nearest(self, guess_vector, guesses):
        """
        Retrieves nearest words to guess_vector, skipping already-guessed words.
        Doubles top_k each iteration if all candidates have already been guessed.
        """
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

            # All returned words were already guessed — expand search
            top_k *= 2

            # Safety cap to avoid infinite loop if vocabulary is exhausted
            if top_k > 1000:
                return self._get_random_word()

    def _get_random_word(self):
        """Fallback: pick a random word from the vocabulary."""
        words = self.vector_search.get_word_list(self.language)
        if words:
            return random.choice(words)
        return "doctor"  # extreme fallback
