"""
PHASE 6: Generate Flashcards with Ollama and SQLite
Steps:
1. Read vocabulary from database
2. Filter by target levels (B2 by default)
3. Check existing flashcards to avoid duplicates
4. Generate sentences with Ollama for new words
5. Save to database
"""

import sqlite3
import requests

DB_PATH = 'data/linguacopilot.db'
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL = 'llama3.2:3b'
TARGET_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']


def get_words_to_process():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    placeholders = ','.join('?' * len(TARGET_LEVELS))
    cursor.execute(f"""
    SELECT v.word, v.level, v.count
    FROM vocabulary v
    LEFT JOIN flashcards f ON v.word = f.word
    WHERE v.level IN ({placeholders}) AND f.word IS NULL
    ORDER BY v.count DESC
    """, TARGET_LEVELS)
    
    words = cursor.fetchall()
    conn.close()
    
    return words


def get_existing_count():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    placeholders = ','.join('?' * len(TARGET_LEVELS))
    cursor.execute(f"SELECT COUNT(*) FROM flashcards WHERE level IN ({placeholders})", TARGET_LEVELS)
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count


def generate_flashcard(word):
    prompt = f"""Create ONE simple German sentence using the word "{word}".
Then provide the French translation.
Format EXACTLY as: German sentence | French translation
Do NOT add any explanation. Do NOT write "Here is..." or "Hier ist..." or any preamble.
Example format: Ich esse Käse. | Je mange du fromage.

Now create for the word: {word}"""

    payload = {
        'model': MODEL,
        'prompt': prompt,
        'stream': False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        data = response.json()
        text = data['response'].strip()
        
        lines = text.split('\n')
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) == 2:
                    german = parts[0].strip().strip('[]').strip('"').strip()
                    french = parts[1].strip().strip('[]').strip('"').strip()
                    
                    if german and french and len(german) > 3 and len(french) > 3:
                        return german, french
        
        return None, None
            
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return None, None


def save_flashcard(word, level, sentence_de, sentence_fr):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO flashcards (word, level, sentence_de, sentence_fr)
    VALUES (?, ?, ?, ?)
    """, (word, level, sentence_de, sentence_fr))
    
    conn.commit()
    conn.close()


def main():
    existing = get_existing_count()
    words = get_words_to_process()
    
    print(f"📚 Existing flashcards: {existing}")
    print(f"🤖 Generating flashcards for {len(words)} NEW words (levels: {', '.join(TARGET_LEVELS)})...")
    
    if len(words) == 0:
        print("✅ No new words to generate!")
        return
    
    success = 0
    
    for i, (word, level, count) in enumerate(words, 1):
        print(f"  {i}/{len(words)} - {word} ({level})... ", end='', flush=True)
        
        german, french = generate_flashcard(word)
        
        if german and french:
            save_flashcard(word, level, german, french)
            success += 1
            print("✅")
        else:
            print("❌")
    
    print(f"\n✅ Generated {success} new flashcards")
    print(f"✅ Total flashcards in DB: {existing + success}")


if __name__ == '__main__':
    main()
