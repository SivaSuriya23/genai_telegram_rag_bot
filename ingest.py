import os
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer

DB_PATH = "data/vectors.db"
DOC_PATH = "data/docs"
MODEL_NAME = "all-MiniLM-L6-v2"

def chunk_text(text, chunk_size=400):
    words = text.split()
    chunks, chunk = [], []
    for word in words:
        chunk.append(word)
        if len(" ".join(chunk)) >= chunk_size:
            chunks.append(" ".join(chunk))
            chunk = []
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks

def ingest():
    model = SentenceTransformer(MODEL_NAME)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_name TEXT,
        content TEXT,
        vector BLOB
    )
    """)

    for file in os.listdir(DOC_PATH):
        with open(os.path.join(DOC_PATH, file), "r", encoding="utf-8") as f:
            text = f.read()
            chunks = chunk_text(text)

            for chunk in chunks:
                emb = model.encode(chunk).astype(np.float32).tobytes()
                cur.execute(
                    "INSERT INTO embeddings (doc_name, content, vector) VALUES (?, ?, ?)",
                    (file, chunk, emb)
                )

    conn.commit()
    conn.close()
    print("Documents ingested successfully.")

if __name__ == "__main__":
    ingest()
