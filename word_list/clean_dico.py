import csv

INPUT_CSV = "dico.csv"
OUTPUT_FILE = "dico_words.txt"

def clean_dico():
    print(f"Reading {INPUT_CSV}...")
    words = set()
    
    try:
        with open(INPUT_CSV, mode="r", encoding="utf-8") as f:
            # We skip the first line if it's not a header, but dico.csv starts with Mot,Définitions
            reader = csv.DictReader(f)
            for row in reader:
                word = row.get("Mot", "").strip()
                
                if not word:
                    continue
                
                # Filter: words that have more than one word (spaces or hyphens)
                # or anything besides letters (numbers, special characters)
                if not word.isalpha():
                    continue
                
                # Filter: words shorter than 3 letters
                if len(word) < 3:
                    continue
                
                words.add(word)
                
    except FileNotFoundError:
        print(f"Error: {INPUT_CSV} not found.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    print(f"Sorting {len(words)} unique words...")
    sorted_words = sorted(list(words))

    print(f"Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, mode="w", encoding="utf-8") as f:
        f.write("\n".join(sorted_words) + "\n")

    print("Done!")

if __name__ == "__main__":
    clean_dico()
