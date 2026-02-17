import sys
import os
import select
import time

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine import GameSession

def input_with_timeout(prompt, timeout):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().strip()
    else:
        sys.stdout.write("\n")  # Move to next line after timeout
        return None

def main():
    print("Welcome to Cemantix Multiplayer!")
    
    # Language Selection
    print("Select Language:")
    print("1. English (en)")
    print("2. French (fr)")
    print("3. Arabic (ar)")
    choice = input("Enter choice (1-3) [default: 1]: ").strip()
    lang_map = {'1': 'en', '2': 'fr', '3': 'ar', 'en': 'en', 'fr': 'fr', 'ar': 'ar'}
    language = lang_map.get(choice, 'en')
    
    # Category Selection
    print("\nSelect Category:")
    print("1. Mixed (All Words)")
    print("2. Sports")
    print("3. History")
    print("4. Science")
    print("5. Computer Science")
    cat_choice = input("Enter choice (1-5) [default: 1]: ").strip()
    cat_map = {'1': None, '2': 'sports', '3': 'history', '4': 'science', '5': 'computer_science'}
    category = cat_map.get(cat_choice, None)
    
    print(f"\nInitializing Game in {language} (Category: {category if category else 'Mixed'})...")
    game = GameSession(language=language, category=category)
    print(f"Goal Word Selected: {game.goal_word} (Hidden)")
    
    # Player Setup
    num_players = 0
    while num_players < 1 or num_players > 4:
        try:
            num_players = int(input("\nHow many players? (1-4): "))
        except ValueError:
            pass
            
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ").strip() or f"Player {i+1}"
        game.add_player(name)
        
    print("\n--- GAME START ---")
    if num_players > 1:
        print("Each player has 15 seconds to guess!")
    else:
        print("No timer for single player mode.")
    
    turn = 0
    game_over = False
    
    while not game_over:
        current_player_idx = turn % num_players
        current_player = game.players[current_player_idx]
        
        print(f"\n>> {current_player.name}'s Turn! (Score: {current_player.score:.2f})")
        
        if num_players > 1:
            guess = input_with_timeout("Enter guess: ", 15)
        else:
            guess = input("Enter guess (or 'quit' to exit): ").strip()
            if not guess: guess = "" # Handle empty input for single player manually if needed
        
        
        if guess is None:
            print("TIMEOUT! Turn skipped.")
        elif guess.lower() == 'quit':
            print("Game aborted.")
            break
        elif not guess.strip():
            print("Empty guess. Turn skipped.")
        else:
            result = game.make_guess(current_player_idx, guess)
            if not result.get('is_valid', True):
                print(f"ERROR: '{result['word']}' does not exist in the game vocabulary!")
                continue

            print(f"Word: {result['word']}")
            print(f"Similarity: {result['similarity']:.4f}")
            print(f"Score Gained: +{result['score_gain']:.2f}")
            if result['notes']:
                print(f"Bonuses: {result['notes']}")
            print(f"Total Score: {current_player.score:.2f}")
            
            if game.winner:
                print(f"\n!!! {current_player.name} WON THE GAME !!!")
                print(f"The word was: {game.goal_word}")
                game_over = True

        turn += 1
        
    print("\n--- LEADERBOARD ---")
    sorted_players = sorted(game.players, key=lambda p: p.score, reverse=True)
    for idx, p in enumerate(sorted_players):
        print(f"{idx+1}. {p.name}: {p.score:.2f}")

if __name__ == "__main__":
    main()
