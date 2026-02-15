import sqlite3

conn = sqlite3.connect('data/linguacopilot.db')
cursor = conn.cursor()

print("=== VIDEOS ===")
cursor.execute("SELECT COUNT(*) FROM videos")
print(f"Total videos: {cursor.fetchone()[0]}")

print("\n=== VOCABULARY ===")
cursor.execute("SELECT COUNT(*) FROM vocabulary")
print(f"Total words: {cursor.fetchone()[0]}")

cursor.execute("SELECT level, COUNT(*) FROM vocabulary GROUP BY level")
for level, count in cursor.fetchall():
    print(f"  {level}: {count}")

print("\n=== FLASHCARDS ===")
cursor.execute("SELECT COUNT(*) FROM flashcards")
print(f"Total flashcards: {cursor.fetchone()[0]}")

cursor.execute("SELECT level, COUNT(*) FROM flashcards GROUP BY level")
for level, count in cursor.fetchall():
    print(f"  {level}: {count}")

print("\n=== TOP 10 A1 WORDS ===")
cursor.execute("SELECT word, count FROM vocabulary WHERE level='A1' ORDER BY count DESC LIMIT 10")
for word, count in cursor.fetchall():
    print(f"  {word}: {count}")

conn.close()

