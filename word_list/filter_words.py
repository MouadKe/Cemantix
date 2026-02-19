from wordfreq import zipf_frequency, top_n_list

INPUT_FILE = "words_alpha.txt"
OUTPUT_FILE = "words_clean.txt"

# Base frequency threshold
# Higher = stricter, fewer words
FREQUENCY_THRESHOLD = 3.0

# Pre-load common words for validation
# This helps remove obscure acronyms and dictionary fossils
COMMON_WORDS = set(top_n_list("en", 50000))


def load_words(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f]


def is_valid_length(word):
    return 3 <= len(word) <= 15


def remove_plural_if_singular_exists(word, word_set):
    """
    Remove simple plural forms if singular exists.
    Avoids deleting words like 'gas', 'bias', etc.
    """
    if word.endswith("s") and word[:-1] in word_set:
        return False
    return True


def is_common_word(word):
    """
    Remove acronyms and rare dictionary fossils
    using real language frequency with dynamic thresholds.
    """
    length = len(word)
    # Stricter thresholds for shorter words to catch acronyms (abc, aclu, etc.)
    if length == 3:
        threshold = 4.5
    elif length == 4:
        threshold = 4.0
    else:
        threshold = FREQUENCY_THRESHOLD

    return zipf_frequency(word, "en") >= threshold


def filter_words(words):
    word_set = set(words)
    filtered = []

    for word in words:
        word = word.lower()

        # Only letters
        if not word.isalpha():
            continue

        # Length filter
        if not is_valid_length(word):
            continue

        # Cross-reference with common words
        # This is a strong signal for valid game words
        if word not in COMMON_WORDS:
            continue

        # Remove simple plural
        if not remove_plural_if_singular_exists(word, word_set):
            continue

        # Remove acronyms / rare words with dynamic thresholds
        if not is_common_word(word):
            continue

        filtered.append(word)

    return sorted(set(filtered))


def save_words(words, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(words))


def main():
    print("Loading words...")
    words = load_words(INPUT_FILE)
    print(f"Original count: {len(words)}")

    print("Filtering...")
    filtered = filter_words(words)

    print(f"Filtered count: {len(filtered)}")

    save_words(filtered, OUTPUT_FILE)

    print(f"Saved clean list to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
