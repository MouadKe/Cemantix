import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

INPUT_FILE = "words_clean.txt"
PACKS_DIR = "packs"
MODEL_NAME = "all-MiniLM-L6-v2"

THEMES = {
    "sports": ["sports", "game", "athlete", "competition", "stadium"],
    "history": ["history", "war", "king", "revolution", "century", "ancient"],
    "science": ["science", "physics", "biology", "chemistry", "experiment", "discovery"],
    "computer_science": ["computer", "programming", "software", "algorithm", "database"]
}

# Similarity threshold (0.0 to 1.0)
# Higher = tighter theme
THRESHOLD = 0.5

def create_packs():
    if not os.path.exists(PACKS_DIR):
        os.makedirs(PACKS_DIR)

    print(f"Loading model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Loading word list: {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]

    print(f"Embedding {len(words)} words... (this might take a minute)")
    word_embeddings = model.encode(words, batch_size=128, show_progress_bar=True)

    for theme_name, keywords in THEMES.items():
        print(f"Processing theme: {theme_name}...")
        
        # Embed theme keywords and take the mean to get a robust theme vector
        theme_vectors = model.encode(keywords)
        theme_vector = np.mean(theme_vectors, axis=0).reshape(1, -1)

        # Calculate similarities
        similarities = cosine_similarity(word_embeddings, theme_vector).flatten()

        # Filter words
        pack_with_sim = sorted(
            [(words[i], similarities[i]) for i in range(len(words)) if similarities[i] >= THRESHOLD],
            key=lambda x: x[1],
            reverse=True
        )
        
        output_path = os.path.join(PACKS_DIR, f"{theme_name}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join([pw[0] for pw in pack_with_sim]))

        print(f"Created {theme_name} pack with {len(pack_with_sim)} words.")
        print(f"Top 5 samples: {[pw[0] for pw in pack_with_sim[:5]]}")

if __name__ == "__main__":
    create_packs()
