import sqlite3
import os

DB_PATH = "chunks.db"
INPUT_FILE = "input.txt"

CHUNK_SIZE = 1000      # words per chunk
OVERLAP = 100          # overlap between chunks


# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    DROP TABLE chunks
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        result TEXT,
        retries INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# --- Chunking Logic ---
def split_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        start = end - overlap  # sliding window

    return chunks


# --- Import Function ---
def import_text(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = split_into_chunks(text)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for chunk in chunks:
        cursor.execute(
            "INSERT INTO chunks (content, status) VALUES (?, 'pending')",
            (chunk,)
        )

    conn.commit()
    conn.close()

    print(f"Imported {len(chunks)} chunks into database.")

# --- Debug Print Function ---
def debug_print():
    conn = sqlite3.connect("chunks.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, status, content FROM chunks LIMIT 5")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()

# --- Main ---
if __name__ == "__main__":
    init_db()
    import_text(INPUT_FILE)
    debug_print()
