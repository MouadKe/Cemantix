import csv
import unicodedata
from wordfreq import zipf_frequency, top_n_list

INPUT_CSV = "dico.csv"
OUTPUT_FILE = "words_fr_clean.txt"

# Tighter frequency threshold for higher quality
# Targeting ~10k-15k words
FREQUENCY_THRESHOLD = 3.5

# Pre-load common French words for validation
# This helps remove obscure dictionary fossils
COMMON_FRENCH_WORDS = set(top_n_list("fr", 40000))


def strip_accents(text):
    """
    Remove accents from a string. e.g., 'été' -> 'ete'
    """
    return "".join(
        c
        for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def is_valid_french_word(word):
    """
    Check if a word is a single word (no spaces/hyphens) and contains only letters.
    """
    if not word:
        return False

    # Check for spaces or hyphens (one word requirement)
    if " " in word or "-" in word:
        return False

    # Use strip_accents to check isalpha safely for accented characters
    if not strip_accents(word).isalpha():
        return False

    return True


def remove_variations(word, word_set):
    """
    Remove common French variations if the root word exists.
    - Feminines: e (grande -> grand)
    - Plurals: s (chats -> chat)
    - Feminine Plurals: es (grandes -> grand)
    """
    # Simple plural
    if word.endswith("s") and word[:-1] in word_set:
        return False

    # Simple feminine
    if word.endswith("e") and word[:-1] in word_set:
        # Avoid removing common short words like 'elle' if 'ell' doesn't exist (handled by in word_set)
        return False

    # Feminine plural
    if word.endswith("es") and word[:-2] in word_set:
        return False

    return True


def is_common_fr_word(word):
    """
    Remove rare words using real language frequency with dynamic thresholds.
    """
    length = len(word)
    # Stricter thresholds for shorter words to avoid junk
    if length <= 3:
        threshold = 4.5
    elif length == 4:
        threshold = 4.0
    else:
        threshold = FREQUENCY_THRESHOLD

    return zipf_frequency(word, "fr") >= threshold


def process_french_dictionary():
    print(f"Loading {INPUT_CSV}...")
    word_candidates = set()

    try:
        with open(INPUT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row.get("Mot", "").strip()
                if not word:
                    continue

                if not is_valid_french_word(word):
                    continue

                word_lower = word.lower()

                # Length filter
                if not (3 <= len(word_lower) <= 15):
                    continue

                if word_lower not in COMMON_FRENCH_WORDS:
                    continue

                if not is_common_fr_word(word_lower):
                    continue

                word_candidates.add(word_lower)

    except FileNotFoundError:
        print(f"Error: {INPUT_CSV} not found.")
        return
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return

    # Second pass: Strip redundant variations (plurals/feminines)
    print("Stripping variations...")
    final_words = set()
    for word in sorted(list(word_candidates)):
        if remove_variations(word, word_candidates):
            # Final step: Strip accents for the output file
            final_words.add(strip_accents(word))

    filtered = sorted(list(final_words))
    print(f"Final Count: {len(filtered)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered))

    print(f"Saved fine-tuned French list to: {OUTPUT_FILE}")


if __name__ == "__main__":
    process_french_dictionary()
