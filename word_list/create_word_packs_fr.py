import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

INPUT_FILE = "words_fr_clean.txt"
PACKS_DIR = "packs_fr"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

THEMES = {
    "sports": ["sport", "athletisme", "competition", "stade", "foot", "tennis"],
    "history": ["histoire", "medieval", "antique", "revolution", "dynastie", "archeologie", "historique"],
    "science": ["science", "physique", "biologie", "chimie", "laboratoire", "astronomie", "scientifique"],
    "computer_science": ["informatique", "ordinateur", "programmation", "logiciel", "algorithme", "code"]
}

# Similarity threshold (0.0 to 1.0)
# Balanced for French multilingual model
THRESHOLD = 0.70

def create_packs():
    if not os.path.exists(PACKS_DIR):
        os.makedirs(PACKS_DIR)

    print(f"Loading multilingual model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Loading French word list: {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]

    print(f"Embedding {len(words)} French words... (this might take a minute)")
    word_embeddings = model.encode(words, batch_size=128, show_progress_bar=True)

    for theme_name, keywords in THEMES.items():
        print(f"Processing theme: {theme_name}...")
        
        # Embed theme keywords
        theme_vectors = model.encode(keywords)
        theme_vector = np.mean(theme_vectors, axis=0).reshape(1, -1)

        # Calculate similarities
        similarities = cosine_similarity(word_embeddings, theme_vector).flatten()

        # Filter and sort
        pack_with_sim = sorted(
            [(words[i], similarities[i]) for i in range(len(words)) if similarities[i] >= THRESHOLD],
            key=lambda x: x[1],
            reverse=True
        )
        
        output_path = os.path.join(PACKS_DIR, f"{theme_name}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join([pw[0] for pw in pack_with_sim]))

        print(f"Created {theme_name} French pack with {len(pack_with_sim)} words.")
        print(f"Top 5 samples: {[pw[0] for pw in pack_with_sim[:5]]}")

if __name__ == "__main__":
    create_packs()
