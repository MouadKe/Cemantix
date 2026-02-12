# Project AI

# Project description

A Cemantix-style game where players guess words and get similarity scores as feedback.

# Ideas

## Competitive guessing

the game can be played by multiple players at once where there are turns each player can guess a word in his turn and he can see what others guessed . 

the winner will be decided with a score of who guessed the most amount of words close to the winning word thus stealing the final word is not as important but rather guessing close to the goal 
the final word will earn you additional 200 score points 

## Leaderboard

a leaderboard where whoever guessed the word faster gets better class 

## Human vs Bot

create 3 bots with different difficulties

### Noob

a bot  

### Pro

first we guess two words to know which direction we will be moving then we move towards the goal big steps at the start and smaller when we get closer 

### Hacker

we use two random guesses and calculate the exact distance away from the goal using the score given to get the size of step , making it far more accurate and doesn’t waste guesses

## Triple language

add french arabic and english 

## Word packs

which are themes that limit the set of words that can be the target words 

### List of themes

- Sports
- History
- Science
- Computer Science
- Darja ( gonna be hard but we got this )

## Different Angle Bonus

If a player guesses 2 words of the similarity to the goal word but not similar to each other {equivalant to guessing another aspect of the main word) they get an extra bonus in points.

Goal: Doctor

Word 1: Medicine

Word 2: Proffession 

## Best on board

In addition we’ll add a bonus for the player with the best word on the board, this adds a special risk of trying to overthrow them and hitting the real word and ending the game (obviously the correct word does not count to this leaderboard).

---

# Specific Game Implementation

## Game Constants

All numbers here can be changed, the ones im putting can be considered placeholders for now.

This section is for the different game constants such as:

Correct Word Guess: +200 pt

Partial Word Guess: Up to +100pt scaled on similarity

Different Angle Bonus: +80pt

Best On Board: +50pt

## Tech Stack

## Front-end

We’ll use the top tier best of the world brainrot slop stack.

- React.js
- Shadcn/ui or radix/ui depending on which UI we going for
- Tailwindcss, lucide-react, GSAP and other helpful libraries.

We’ll then statically build the website using vite to serve it from our backend.

## Back-end

Alright here we go for the real shit

- Backend Framework (Python):
    - Django
    - Pros/Cons
        
        **PROS:**
        
        - I, iman am used to it and how it works and is setup
        - It is very easy to get rolling and doesnt take much boiler plate
        
        **CONS:**
        
        - Mostly made for quick API’s not a real backend service
        - Doesnt have all the features a real backend Framework might have
    - Flask
    - Pros/Cons
        
        **PROS:**
        
        - Is a full fledged backend framework so it should have more features than FASTAPI
        
        **CONS:**
        
        - Neither of us ever used it and I dont have any idea about how it is to code using it
- Database
    - Users and general data, either:
        - MongoDB Atlas
        - PostegreSQL Through Supabase or Convex
        - Similarity Search for word Embedding (vectorDBs):w
        - ChromaDB — Simple to use, but I had problems with making it work in the past
    

### Other Notes on the backend

- The server will have full authority on the game state obviously
- Joining and experiencing the games will be done through Web Sockets because Pooling doesn’t make sense in this case (Also I always wanted to make a WS API)
- Authentication Should be done through some library like Clerk or something.
- We’ll obviously host the app for extra credit (We’ll use render)
- For the Embedding Model I think We’ll be forced to use a Smaller One from Hugging Face due to limitations by Render.
- If we dont use an auth library well use a simple JWT Auth Server.

### Rough Backend API

Very Much Subject to change

**Authentication API (/auth)**

- *POST /signup*
- *POST /login*
- *DELETE /account*
- *POST /refresh*

**Game API (Needs logged in user) (/games)**

- *GET /rooms*
- *POST /rooms*
- *POST /join*
- *POST /leave*

**LeaderBoard API  (/leader)**

- *GET /*

**Bots API (/bot):**

- *POST /guess*

(We send the entire game state here such as what the bot has guessed and stuff and what tier of bot)

**Internal game packets**

- WORD_GUESS
- GUESS_SCORE
- DIFFERENT_ANGLE
- NEW_BEST_BOARD
- SCORE_UPDATED
- PLAYER_JOINED
- PLAYER_LEFT
- GAME_END
- FINAL_SCORES