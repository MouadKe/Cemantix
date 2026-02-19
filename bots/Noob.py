import numpy as np
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_logic.services import WordSimilarityService


class NoobBot:
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

        # Step 2: Sort by similarity ascending
        sorted_guesses = sorted(guesses, key=lambda x: x["similarity"])

        # Step 3: Take the two best guesses
        g1 = sorted_guesses[-2]  # second best
        g2 = sorted_guesses[-1]  # best

        # Step 4: Embed both words into vectors
        v1 = self.vector_search.get_word_vector(g1["word"], self.language)
        v2 = self.vector_search.get_word_vector(g2["word"], self.language)

        if v1 is None or v2 is None:
            return self._get_random_word()

        # Step 5: Estimate direction toward target
        direction = v2 - v1

        # Step 6: Step forward from best guess
        step_size = 0.5
        guess_vector = v2 + step_size * direction

        # Step 7: Normalize
        norm = np.linalg.norm(guess_vector)
        if norm > 0:
            guess_vector = guess_vector / norm

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
            if top_k > 10_000:
                return self._get_random_word()

    def _get_random_word(self):
        """Fallback: pick a random word from the vocabulary."""
        words = self.vector_search.get_word_list(self.language)
        if words:
            return random.choice(words)
        return "doctor"  # extreme fallback
