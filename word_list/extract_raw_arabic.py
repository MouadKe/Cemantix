import json
import os
import glob

OUTPUT_DIR = "vocabulary"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ar_raw.txt")

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

def extract_raw():
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

    print(f"Extracted {len(all_words)} raw unique words.")
    
    print(f"Saving to {OUTPUT_FILE}...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # Save all words sorted alphabetically
        f.write("\n".join(sorted(list(all_words))) + "\n")
        
    print("Done!")

if __name__ == "__main__":
    extract_raw()
