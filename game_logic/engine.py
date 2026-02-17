import random
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
        
        # Dictionaries for different languages and categories
        self.dictionaries = {
            'en': {
                'general': ["apple", "banana", "cherry", "doctor", "medicine", "hospital", "nurse", "patient", "computer", "python", "code"],
                'sports': ["football", "soccer", "basketball", "tennis", "stadium", "athlete", "goal", "tournament"],
                'history': ["war", "empire", "king", "revolution", "ancient", "museum", "civilization", "history"],
                'science': ["physics", "chemistry", "biology", "atom", "energy", "experiment", "laboratory", "scientist"],
                'computer_science': ["algorithm", "database", "network", "software", "hardware", "programming", "internet", "security"]
            },
            'fr': {
                'general': ["pomme", "banane", "cerise", "médecin", "médicament", "hôpital", "infirmière", "patient", "ordinateur", "python", "code"],
                'sports': ["football", "tennis", "basketball", "stade", "athlète", "but", "tournoi", "sport"],
                'history': ["guerre", "empire", "roi", "révolution", "ancien", "musée", "civilisation", "histoire"],
                'science': ["physique", "chimie", "biologie", "atome", "énergie", "expérience", "laboratoire", "scientifique"],
                'computer_science': ["algorithme", "données", "réseau", "logiciel", "matériel", "programmation", "internet", "sécurité"]
            },
            'ar': {
                'general': ["تفاح", "موز", "كرز", "طبيب", "دواء", "مستشفى", "ممرضة", "مريض", "حاسوب", "بايثون", "كود"],
                'sports': ["كرة القدم", "تنس", "كرة السلة", "ملعب", "رياضي", "هدف", "بطولة", "رياضة"],
                'history': ["حرب", "إمبراطورية", "ملك", "ثورة", "قديم", "متحف", "حضارة", "تاريخ"],
                'science': ["فيزياء", "كيمياء", "أحياء", "ذرة", "طاقة", "تجربة", "مختبر", "عالم"],
                'computer_science': ["خوارزمية", "بيانات", "شبكة", "برمجيات", "أجهزة", "برمجة", "إنترنت", "أمن"]
            }
        }
        
        lang_dicts = self.dictionaries.get(language, self.dictionaries['en'])
        
        if category and category in lang_dicts:
            self.dictionary = lang_dicts[category]
        else:
            self.dictionary = []
            for words in lang_dicts.values():
                self.dictionary.extend(words)
            self.dictionary = list(set(self.dictionary))
        
        # Load model immediately
        print(f"Loading model for {language}...")
        self.similarity_service.load_model(language)
        
        self.goal_word = goal_word if goal_word else random.choice(self.dictionary)
        self.players = []
        self.global_best_similarity = 0.0
        self.winner = None

    def add_player(self, name):
        self.players.append(Player(name))

    def make_guess(self, player_idx, word):
        player = self.players[player_idx]
        word = word.lower().strip()
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

        # 4. Different Angle Bonus (+80) - Simplified
        # Check if new guess is similar to goal (>0.5) but not similar to ANY previous guess of the same player (<0.5)
        # Only if it's a good guess
        if similarity > 0.5:
            is_different_angle = True
            for prev_guess in player.guesses:
                # We interpret duplicate words as not being a different angle.
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
            "notes": ", ".join(notes)
        }
        return guess_result
