import json
import os
import glob
from wordfreq import word_frequency

OUTPUT_DIR = "vocabulary"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ar_clean.txt")
FREQ_THRESHOLD = 1e-7  # Adjust this threshold to define "rare"

def extract_words(data):
    words = set()
    if isinstance(data, dict):
        for value in data.values():
            words.update(extract_words(value))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                words.add(item.strip())
            else:
                words.update(extract_words(item))
    return words

def clean_arabic():
    all_words = set()
    
    # Process all JSON files in the current directory
    json_files = glob.glob("*.json")
    
    for filename in json_files:
        print(f"Loading {filename}...")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                words = extract_words(data)
                all_words.update(words)
        except Exception as e:
            print(f"Error loading {filename}: {e}")

    print(f"Extracted {len(all_words)} unique words.")
    
    cleaned_words = []
    print("Filtering words...")
    
    # Prefix for "Al-" in Arabic: Alif (0627) + Lam (0644)
    PREFIX_AL = '\u0627\u0644'
    
    for word in all_words:
        # Filter: starts with "ال"
        if word.startswith(PREFIX_AL):
            continue
            
        # Filter: rare words
        # wordfreq documentation suggests that words not in the database have frequency 0
        freq = word_frequency(word, 'ar')
        if freq < FREQ_THRESHOLD:
            continue
            
        cleaned_words.append(word)

    print(f"After filtering: {len(cleaned_words)} words remaining.")
    
    print(f"Saving to {OUTPUT_FILE}...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(cleaned_words)) + "\n")
        
    print("Done!")

if __name__ == "__main__":
    clean_arabic()
