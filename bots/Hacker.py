import numpy as np
import random
from game_logic.services import WordSimilarityService
from game_logic.vector_db import VectorDB


class HackerBot:
    def __init__(self, language='en'):
        self.language = language
        self.similarity_service = WordSimilarityService()
        self.vector_search = VectorDB()

    def get_next_guess(self, guesses, scoreboard, pack, bot_id):
        """
        guesses:    List of dicts {"word": str, "similarity": float}
        scoreboard: dict {player_id: score}
        pack:       "sports" | "history" | "science" | "computer_science" | "mixed"
        bot_id:     identifier of this bot in the scoreboard
        Returns the bot's next guess as a string.
        """
        # Step 1: Determine mode
        mode = self._choose_strategy(scoreboard, bot_id)

        # Step 2: Not enough data → themed guess instead of pure random
        if len(guesses) < 2:
            return self._themed_guess(pack, guesses)

        # Step 3: Check if stuck (best similarity hasn't improved much recently)
        is_stuck = self._is_stuck(guesses)
        
        if is_stuck:
            # Panic mode: Try to find a completely new angle first
            word = self._find_different_angle(guesses)
            if word:
                return word
                
            # If no different angle found, try a themed guess if applicable
            if pack and pack != "mixed":
                return self._themed_guess(pack, guesses)
                
            # Last resort: random word
            return self._get_random_word()

        # Step 4: Aggressive mode — try special strategies first
        if mode == "aggressive":
            # Strategy 1: find a word from a different angle
            word = self._find_different_angle(guesses)
            if word:
                return word

            # Strategy 2: play around the best guess region
            best = max(guesses, key=lambda x: x["similarity"])
            v_best = self.vector_search.get_word_vector(best["word"], self.language)
            if v_best is not None:
                word = self._play_around_target(v_best, guesses)
                if word:
                    return word

        # Step 5: Normal mode (or aggressive fallback) → Pro Bot logic
        return self._pro_bot_guess(guesses)

    def _is_stuck(self, guesses):
        """Returns True if the best similarity hasn't improved in the last 3 turns."""
        if len(guesses) < 5:
            return False
            
        recent_best = max([g["similarity"] for g in guesses[-3:]], default=0)
        overall_best = max([g["similarity"] for g in guesses[:-3]], default=0)
        
        # If we haven't beaten the previous best by at least 0.5 in 3 turns, we are stuck
        # (Assuming similarity is 0-100 scale)
        if recent_best <= overall_best + 0.5:
             # Also check if the best similarity is low (< 40). 
             if overall_best < 40:
                 return True
                 
        return False

    # ─── Strategy Selection ───────────────────────────────────────────────────

    def _choose_strategy(self, scoreboard, bot_id):
        """Switch to aggressive if the bot is behind the leader."""
        bot_score = scoreboard.get(bot_id, 0)
        max_score = max(scoreboard.values()) if scoreboard else 0
        if bot_score < max_score:
            return "aggressive"
        return "normal"

    # ─── Strategy 1: Different Angle ─────────────────────────────────────────

    def _find_different_angle(self, guesses):
        """
        Find a candidate near the best guess that is dissimilar
        to all high-scoring guesses (cosine sim < 0.6).
        """
        high_guesses = [g for g in guesses if g["similarity"] >= 50]
        if not high_guesses:
            return None

        guess_vectors = []
        for g in high_guesses:
            v = self.vector_search.get_word_vector(g["word"], self.language)
            if v is not None:
                guess_vectors.append(v)

        if not guess_vectors:
            return None

        best = max(guesses, key=lambda x: x["similarity"])
        v_best = self.vector_search.get_word_vector(best["word"], self.language)
        if v_best is None:
            return None

        guessed_words = {g["word"].lower() for g in guesses}

        # Search broad neighborhood of the best guess, but looking for DIFFERENT words
        top_k = 100
        while True:
            candidates = self.vector_search.get_nearest_word(
                v_best, self.language, top_k=top_k
            )
            if not candidates:
                return None

            for candidate in candidates:
                if candidate.lower() in guessed_words:
                    continue
                    
                v = self.vector_search.get_word_vector(candidate, self.language)
                if v is None:
                    continue
                
                # Check orthogonality/dissimilarity to other high scoring words
                is_different = True
                for gv in guess_vectors:
                    sim = np.dot(v, gv)
                    if sim > 0.6: # If >0.6 similarity to any other good guess, it's not "different" enough
                        is_different = False
                        break
                
                if is_different:
                    return candidate

            # No valid candidate found in this range — expand
            if top_k >= 2000:
                return None
            top_k *= 2

    # ─── Strategy 2: Play Around Target ──────────────────────────────────────

    def _play_around_target(self, best_vector, guesses):
        """Exploit the high-similarity region by guessing words close to current best."""
        guessed_words = {g["word"].lower() for g in guesses}
        top_k = 10

        while True:
            candidates = self.vector_search.get_nearest_word(
                best_vector, self.language, top_k=top_k
            )
            if not candidates:
                return None

            for candidate in candidates:
                if candidate.lower() not in guessed_words:
                    return candidate

            if top_k >= 2000:
                return None
            top_k *= 2

    # ─── Strategy 3: Theme-Based Guessing ────────────────────────────────────

    def _themed_guess(self, pack, guesses):
        """Pick a random word from the active pack if available."""
        if not pack or pack == "mixed":
            return self._get_random_word()
            
        # Try to get words from the specific pack
        pack_words = self.vector_search.get_pack_words(pack, self.language)
        
        guessed_words = {g["word"].lower() for g in guesses}
        candidates = [w for w in pack_words if w not in guessed_words]
        
        if candidates:
            return random.choice(candidates)
            
        return self._get_random_word()

    # ─── Pro Bot Fallback ─────────────────────────────────────────────────────

    def _pro_bot_guess(self, guesses):
        """
        Full Pro Bot logic — weighted target estimation using all guesses.
        Re-implemented here to avoid dependency complications.
        """
        vectors = []
        scores = []
        for g in guesses:
            v = self.vector_search.get_word_vector(g["word"], self.language)
            if v is not None:
                vectors.append(v)
                scores.append(g["similarity"])

        if len(vectors) < 2:
            return self._get_random_word()

        # Weighted estimate of target position (Simple Pro version)
        target_estimate = np.zeros_like(vectors[0])
        for v, s in zip(vectors, scores):
            weight = (s / 100.0) ** 3
            target_estimate += v * weight

        norm = np.linalg.norm(target_estimate)
        if norm == 0:
            return self._get_random_word()
        target_estimate /= norm

        best_guess = max(guesses, key=lambda x: x["similarity"])
        v_best = self.vector_search.get_word_vector(best_guess["word"], self.language)
        if v_best is None:
            return self._get_random_word()

        direction = target_estimate - v_best
        step_size = (100 - best_guess["similarity"]) / 100

        guess_vector = v_best + step_size * direction
        norm = np.linalg.norm(guess_vector)
        if norm == 0:
            return self._get_random_word()
        guess_vector /= norm

        return self._get_unguessed_nearest(guess_vector, guesses)

    # ─── Shared Helpers ───────────────────────────────────────────────────────

    def _get_unguessed_nearest(self, guess_vector, guesses):
        """Find the nearest word not already guessed, expanding search if needed."""
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
