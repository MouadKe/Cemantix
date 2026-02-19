import random
import os
from services import WordSimilarityService

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.guesses = []
        self.best_similarity = -1.0

class GameSession:
    def __init__(self, language='en', category=None, goal_word=None):
        self.similarity_service = WordSimilarityService()
        self.language = language
        self.category = category
        
        # Base paths for word lists
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        word_list_path = os.path.join(base_path, "word_list")
        
        # Path configuration
        self.paths = {
            'en': {
                'packs': os.path.join(word_list_path, "packs"),
                'vocab': os.path.join(word_list_path, "vocabulary", "words_alpha.txt")
            },
            'fr': {
                'packs': os.path.join(word_list_path, "packs_fr"),
                'vocab': os.path.join(word_list_path, "vocabulary", "dico_words.txt")
            },
            'ar': {
                'packs': os.path.join(word_list_path, "packs_ar"),
                'vocab': os.path.join(word_list_path, "vocabulary", "ar_raw.txt")
            }
        }
        
        lang_config = self.paths.get(language, self.paths['en'])
        
        # Load vocabulary for guess validation
        self.vocabulary = self._load_word_set(lang_config['vocab'])
        
        # Load target word pool from packs
        category_name = f"{category}.txt" if category else "mixed.txt"
        pack_path = os.path.join(lang_config['packs'], category_name)
        
        self.target_pool = self._load_word_list(pack_path)
        if not self.target_pool:
            # Fallback if specific pack fails
            fallback_path = os.path.join(lang_config['packs'], "mixed.txt")
            self.target_pool = self._load_word_list(fallback_path)
        
        # Load model immediately
        print(f"Loading model for {language}...")
        self.similarity_service.load_model(language)
        
        self.goal_word = goal_word if goal_word else random.choice(self.target_pool)
        self.players = []
        self.global_best_similarity = 0.0
        self.winner = None

    def _load_word_list(self, filepath):
        """Loads words from a text file into a list."""
        if not os.path.exists(filepath):
            print(f"Warning: File not found: {filepath}")
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return [line.strip().lower() for line in f if line.strip()]
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return []

    def _load_word_set(self, filepath):
        """Loads words from a text file into a set for fast lookup."""
        return set(self._load_word_list(filepath))

    def add_player(self, name):
        self.players.append(Player(name))

    def make_guess(self, player_idx, word):
        player = self.players[player_idx]
        word = word.lower().strip()
        
        # Check if word exists in vocabulary
        if word not in self.vocabulary:
            return {
                "word": word,
                "error": "Word not found in vocabulary",
                "is_valid": False
            }

        similarity = self.similarity_service.get_similarity_to_goal(word, self.goal_word, self.language)
        
        score_gain = 0
        notes = []

        # 1. Correct Word (+200)
        if word == self.goal_word:
            score_gain += 200
            notes.append("CORRECT WORD (+200)")
            self.winner = player
        else:
            # 2. Partial Score
            partial = max(0, similarity * 100)
            score_gain += partial

        # 3. Best on Board (+50)
        if similarity > self.global_best_similarity and word != self.goal_word:
            score_gain += 50
            self.global_best_similarity = similarity
            notes.append("BEST ON BOARD (+50)")

        # 4. Different Angle Bonus (+80)
        if similarity > 0.5:
            is_different_angle = True
            for prev_guess in player.guesses:
                if prev_guess['word'] == word:
                     is_different_angle = False
                     break
                     
                sim_between = self.similarity_service.compute_similarity(word, prev_guess['word'], self.language)
                if sim_between > 0.5:
                    is_different_angle = False
                    break
            
            if is_different_angle and len(player.guesses) > 0:
                 score_gain += 80
                 notes.append("DIFFERENT ANGLE (+80)")

        player.score += score_gain
        if similarity > player.best_similarity:
            player.best_similarity = similarity

        guess_result = {
            "word": word,
            "similarity": similarity,
            "score_gain": score_gain,
            "total_score": player.score,
            "notes": ", ".join(notes),
            "is_valid": True
        }
        player.guesses.append(guess_result)
        return guess_result
