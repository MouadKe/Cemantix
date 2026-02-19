# How to run

First of download the pre-embedded vocabulary and word packs at [link](https://drive.google.com/drive/folders/1VWg5lcZCa7Xpcb33c5Qch0GQHWmoD_iZ?usp=sharing) and extract them and put the .csv files next to their corresponding .txt

> This was done to save some time as not to re embed the words

After this you download the project requirements found in the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

After installing the dependencies just run `game_logic/main.py`

```bash
python game_logic/main.py
```

> For now the application is purely terminal based since the web service version wasn't finished in time.

> [!WARN] OS Compatibility
>
> The game seems to have some issues running on windows

# Game Description

Cemantix is a popular web based game with a simple principle, every day there is a hidden word and you try to guess it.

As feedback to each guess you get a hot/cold style meter showing how similar the 2 words are, not in syntax but in meaning (semantics) thus the name.

# Problem Formulation

Our objective is to try to understand and recreate the underlying systems behind Cemantix whilst adding a new and unique twist to keep it fresh.

# Implementation

## High Overview

Our game is a twist on top of this semantic guessing called sonar, it introduces competitivity into the field by letting multiple players and bots try and solve the same word collecting points during the game to try and win.

## Game Mechanics

### Multiplayer System

The Most basic way of playing sonar is through the multiplayer system, up to 4 players/bots called operators join the game and a hidden word is chosen.

They will then each have a limited amount of tries and time to put their guessed.

Your final score is the addition of your 5 best guesses by default, as to make it not just a who guesses correct first.

### Rounds & Timers

The guesses work by cycling through the players, giving each player a pre determined amount of time to try and submit their guess.

Each guess returns its similarity with the hidden word and an amount of points between 0-100 if no special modifiers are hit.

### Special Modifiers

Special modifiers might happen to some guesses we have the following:

- CORRECT WORD +100: given to when u guess the hidden word, making the guess worth 200 points
- BEST ON BOARD +50: given to the best word that isn't the hidden word on the boa
- DIFFERNET ANGLE +80: given when you guess 2 words with the same similarity to the hidden word but are different from each other

## Bots

> Hacker and Pro Bots are not working as intended.

### Bot Technical Design

This document outlines the technical implementation and strategies for the three bot difficulty levels in Cemantix: **Noob**, **Pro**, and **Hacker**.

#### Common Architecture

All bots share a common foundation:

- **Vector Database (VectorDB)**: Loads pre-trained word embeddings (SentenceTransformers `all-MiniLM-L6-v2`) and normalizes vectors for consistent cosine similarity.
- **Similarity Service**: Computes the dot product between word vectors to determine semantic closeness.
- **Base Class**: They all implement a **get_next_guess(guesses)** method that returns a single word string.

#### 1. Noob Bot (NoobBot)

**Philosophy**: Simulates a beginner player who grasps the basic concept of "warmer/colder" but lacks vocabulary precision.

##### Strategy: Simple Gradient Ascent

- **Input**: Takes the list of all previous guesses.
- **Selection**: Identifies the **Top 2** best guesses so far.
- **Logic**:
  1. Calculates a direction vector from the 2nd best guess to the 1st best guess (`Directory = Best - SecondBest`).
  2. Projects a target vector forward along this path (`Target = Best + Direction * 0.5`).
- **"Clumsiness" Factor**:
  1. Searches for the **Top 50** nearest neighbors to the target vector (instead of just the top 1).
  2. Randomly selects one of the **Top 10** matches.
  - _Effect_: High variance. Sometimes strays from the optimal path, mimicking a limited vocabulary or loose associations.

#### 2. Pro Bot (ProBot)

**Philosophy**: Simulates a competent player who uses logic, avoids bad guesses, and systematically explores semantic neighborhoods.

##### Strategy: Dynamic State Machine

ProBot switches strategies based on its highest similarity score (`best_sim`):

###### Phase 1: Exploration (< 20%)

- **Goal**: Find *any* improved signal.
- **Action**: Makes broad jumps using random words or very loose associations to scatter across the semantic space.

###### Phase 2: Sticky Hill Climbing (20% - 60%)

- **Goal**: Exploit a promising lead without getting distracted.
- **Action**:
  - **Sticky Logic**: If the *last* guess was the highest scoring so far, it strictly explores the immediate neighborhood (nearest unguessed neighbor) of that word.
  - **Gradient Fallback**: If the last guess wasn't an improvement, it uses a stable gradient (`Best - SecondBest`) to find a new direction, similar to Noob but with higher precision (Top 1 selection).

###### Phase 3: Trend Projection (> 60%)

- **Goal**: Pinpoint the target word with high precision.
- **Action**:
  - **Filtering**: Selects only the **Top 5** best guesses to remove noise from early bad guesses.
  - **Centroid Calculation**: Calculates the weighted center of the "rest" (ranks 2-5).
  - **Extrapolation**: Projects a vector from the "Rest Center" through the "Best Guess" (`Direction = Best - RestCenter`).
  - **Dynamic Step**: Adjusts step size (0.2 - 0.5) based on score to avoid overshooting the target.

#### 3. Hacker Bot (HackerBot)

**Philosophy**: Simulates an expert player (or cheater) who uses meta-game knowledge, specific word lists, and aggressive optimization algorithms.

##### Strategy: Aggressive Exploitation & Meta-Gaming

Inherits

ProBot logic for standard play but overrides it with:

###### 1. Stuck Detection & Panic Mode

- **Trigger**: If the best similarity hasn't improved in 3 turns.
- **Action**: Forces a "Teleport" to a new semantic area using:
  - **Themed Guess**: If a specific pack is active (e.g., "Sports"), picks a random word from that pack.
  - **Different Angle**: Finds a word that is orthogonal (mathematically dissimilar) to the current best guesses to break out of local maxima.
  - **Random Jump**: As a last resort, picks a completely random high-frequency word.

###### 2. "Play Around Target" (Aggressive Mode)

- **Trigger**: Score > 90% (Endgame) or Losing Badly (Catch-up).
- **Action**:
  - Searches the **entire vocabulary** for words extremely close to the current best guess.
  - Expands the search radius dynamically until a candidate is found.
  - This mimics a player "brute-forcing" synonyms once they know the exact meaning.

###### 3. Pack Awareness

- **Logic**: Unlike other bots, HackerBot knows which "Pack" (category) is selected and prioritizes words from that specific list (e.g., `football` in a Sports pack) before falling back to general vocabulary.

## Guessing Engine

### Vocabulary

Since this is a language based game we have specified a vocabulary of allowed words to guess, they are based on vocabularies found on the internet with all the words you could ever think of.

### Word Packs

Each word pack was built with a specific theme, it was built using the following process:

- Grabbed Words That have relation with the theme
- Added all words with a high similarity to these seed words
- ran them through a frequency model, this model trained on Wikipedia returns for each word how frequently used it is, with this it helps us eliminate obscure words from the word packs.

### Vector Embeddings

The Main Engine behind all of this magic are vector embeddings the following is what we learnt about them during the project.

#### What is a vector embedding

A vector embedding is a list of numbers that is outputted by what we call `embedding models` these models take as input a word, piece of word or sentence and their job is to encode the "meaning" of that word into a list of numbers.

This list of numbers if we think about it mathematically has a very high dimensionality, this will help us understand the embed vector as having a "meaning" for each direction/dimension.

so one dimension could be "size" so the sentenced "Eiffel Tower" and "Eiffel Tower Trinket" might have similar embeddings in all dimensions but the trinket has much lower value in our "size dimension" of course since most embedding models are Deep Neural Networks we don't really know what dimension is but it is still true since operations like

$E(king) + E(man) - E(woman) = E(queen)$

Does work in some embedding models

#### cosine similarity

Cosine similarity is a mathematical tool that helps us know if two vectors are pointing in the general same direction, in our case a high cosine similarity means high similarity of semantic value and a full match is always the same vector

This is done by measuring the angle between them so the bigger the angle the more different they are.

# Technical Specifications

## Terminal App

The terminal application has the following files:

- `main.py`: main entrance point for the app
- `engine.py`: heart of the game, with all the information about game state
- `services.py`: The embedding engine, to turn guesses back and forth with the embed space
- `bots/`: code for the different bots, this is not working for now

> [!NOTE] Un implemented
>
> From here onwards is unimplemented territory and only half finished, in a different branch called django-transform

## UI Design

Figma Design: [Link](https://www.figma.com/design/rFu8ZcMmH883x1EwWOsZpp/Untitled?node-id=0-1&t=v5URC26X1hKDliFJ-1)

## Backend API

The Backend Works through a docker container with the following service stack:

- **Django API**: Main REST API server
- **MySQL**: database layer
- **chroma**: vector database to store embeds fast

The API layer exposes the following endpoints

| Method  | URL                          | Permission     | Request Body                       | Response                                                              |
| ------- | ---------------------------- | -------------- | ---------------------------------- | --------------------------------------------------------------------- |
| `POST`  | `/games/`                    | Authenticated  | —                                  | `room_id`, `status`, `creator`                                        |
| `POST`  | `/games/{room_id}/join/`     | Authenticated  | —                                  | Full room state                                                       |
| `GET`   | `/games/{room_id}/`          | Player in room | —                                  | Full room state                                                       |
| `PATCH` | `/games/{room_id}/settings/` | Creator only   | `language?`, `word_pack?`, `bots?` | Full room state                                                       |
| `POST`  | `/games/{room_id}/start/`    | Creator only   | —                                  | Full room state                                                       |
| `POST`  | `/games/{room_id}/guess/`    | Player in room | `guess`                            | `username`, `word_score`, `total_score`, `game_over`, `final_scores?` |
| `POST`  | `/games/`                    |                |                                    |                                                                       |
| `POST`  | `/users/register`            | --             | `username`, `password`             | `username`                                                            |
| `POST`  | `/users/login`               | --             | `username`, `password`             | `access_token`, `refresh_token`                                       |
| `POST`  | `/users/refresh`             | --             | `refresh_token`                    | `access_token`                                                        |

# Future Improvements

For Now the app has multiple Issues, we will count those as the main improvement we look forward to implementing

- Finish Creating The Web Service backend
- Fix the problems with the bots not working correctly
- Create the frontend of the application that adheres to the figma design
- Add Semantic Hints to the game
- Add More word packs
- Allow custom word packs
