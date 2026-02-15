"""
PHASE 4: Extract Vocabulary and store in SQLite
Steps:
1. Read all cleaned .txt files
2. Use spaCy for German NLP
3. Classify words by CEFR level
4. Save to database (avoiding duplicates)
"""

import os
import sqlite3
import spacy
from wordfreq import word_frequency

INPUT_DIR = 'data/processed/cleaned'
DB_PATH = 'data/linguacopilot.db'

print("Loading spaCy German model...")
nlp = spacy.load('de_core_news_sm')


def get_cefr_level(word, lang='de'):
    freq = word_frequency(word, lang)
    
    if freq >= 1e-4:
        return 'A1'
    elif freq >= 5e-5:
        return 'A2'
    elif freq >= 1e-5:
        return 'B1'
    elif freq >= 5e-6:
        return 'B2'
    elif freq >= 1e-6:
        return 'C1'
    else:
        return 'C2'


def extract_words(text):
    doc = nlp(text.lower())
    
    words = []
    for token in doc:
        if (token.is_alpha 
            and len(token.text) > 3 
            and not token.is_stop
            and not token.pos_ in ['PROPN', 'NUM', 'PUNCT', 'SYM', 'X']):
            
            lemma = token.lemma_
            level = get_cefr_level(lemma)
            words.append((lemma, level))
    
    return words


def save_to_db(vocabulary):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for word, data in vocabulary.items():
        cursor.execute("""
        INSERT INTO vocabulary (word, level, count)
        VALUES (?, ?, ?)
        ON CONFLICT(word) DO UPDATE SET count = count + ?
        """, (word, data['level'], data['count'], data['count']))
    
    conn.commit()
    conn.close()


def get_db_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT level, COUNT(*) FROM vocabulary GROUP BY level")
    stats = dict(cursor.fetchall())
    
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return total, stats


def main():
    txt_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.txt')]
    
    print(f"📚 Extracting vocabulary from {len(txt_files)} files...")
    
    all_words = []
    
    for i, filename in enumerate(txt_files, 1):
        file_path = os.path.join(INPUT_DIR, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        words = extract_words(text)
        all_words.extend(words)
        print(f"  ✅ {i}/{len(txt_files)} - {len(words)} words")
    
    vocabulary = {}
    for word, level in all_words:
        if word not in vocabulary:
            vocabulary[word] = {'count': 0, 'level': level}
        vocabulary[word]['count'] += 1
    
    save_to_db(vocabulary)
    
    total, stats = get_db_stats()
    
    print(f"\n✅ Saved {len(vocabulary)} unique words to database")
    print(f"✅ Total words in DB: {total}")
    
    print("\n📊 Words by level:")
    for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        count = stats.get(level, 0)
        print(f"  {level}: {count} words")


if __name__ == '__main__':
    main()
