import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

INPUT_FILE = "vocabulary/ar_clean.txt"
PACKS_DIR = "packs_ar"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

THEMES = {
    "sports": ["رياضة", "لعب", "لاعب", "منافسة", "ملعب", "كرة"],
    "history": ["تاريخ", "حرب", "ملك", "ثورة", "قرن", "قديم", "آثار"],
    "science": ["علم", "فيزياء", "بيولوجيا", "كيمياء", "مختبر", "فضاء", "بحث"],
    "computer_science": ["برمجة", "حاسوب", "مطور", "تطبيق", "خوارزمية", "بيانات"]
}

# Similarity threshold (0.0 to 1.0)
# Set to 0.75 for a balance between specificity and variety
THRESHOLD = 0.75

def create_packs():
    if not os.path.exists(PACKS_DIR):
        os.makedirs(PACKS_DIR)

    print(f"Loading multilingual model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Loading Arabic word list: {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]

    print(f"Embedding {len(words)} Arabic words... (this might take some time)")
    # Using a larger batch size for performance
    word_embeddings = model.encode(words, batch_size=256, show_progress_bar=True)

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

        print(f"Created {theme_name} Arabic pack with {len(pack_with_sim)} words.")
        print(f"Top 5 samples: {[pw[0] for pw in pack_with_sim[:5]]}")

if __name__ == "__main__":
    create_packs()
