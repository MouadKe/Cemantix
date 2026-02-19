import numpy as np
import random
from game_logic.services import WordSimilarityService
from game_logic.vector_db import VectorDB


class NoobBot:
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

        # Sort by similarity ascending
        sorted_guesses = sorted(guesses, key=lambda x: x["similarity"])

        # Take the two best guesses
        g1 = sorted_guesses[-2]  # second best
        g2 = sorted_guesses[-1]  # best

        v1 = self.vector_search.get_word_vector(g1["word"], self.language)
        v2 = self.vector_search.get_word_vector(g2["word"], self.language)

        if v1 is None or v2 is None:
            return self._get_random_word()

        # Estimate direction toward target and step forward
        direction = v2 - v1
        step_size = 0.5
        guess_vector = v2 + step_size * direction

        # Normalize
        norm = np.linalg.norm(guess_vector)
        if norm > 0:
            guess_vector = guess_vector / norm

        return self._get_unguessed_nearest(guess_vector, guesses)

    def _get_unguessed_nearest(self, guess_vector, guesses):
        """
        Retrieves nearest words to guess_vector, skipping already-guessed words.
        Simulates 'rough' guessing by picking randomly from top results.
        """
        guessed_words = {g["word"].lower() for g in guesses}
        top_k = 50 
        
        while True:
            nearest_words = self.vector_search.get_nearest_word(
                guess_vector, self.language, top_k=top_k
            )

            if not nearest_words:
                return self._get_random_word()
            
            candidates = [w for w in nearest_words if w.lower() not in guessed_words]
            
            if candidates:
                # Pick randomly from top 10 matches to simulate clumsiness
                return random.choice(candidates[:10]) 

            # All returned words were already guessed — expand search
            top_k *= 2

            if top_k > 10_000:
                return self._get_random_word()

    def _get_random_word(self):
        """Fallback: pick a random word from the vocabulary."""
        words = self.vector_search.get_word_list(self.language)
        if words:
            return random.choice(words)
        return "doctor"  # extreme fallback
