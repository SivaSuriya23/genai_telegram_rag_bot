import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer

DB_PATH = "data/vectors.db"
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve(query, top_k=3):
    q_emb = model.encode(query)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT doc_name, content, vector FROM embeddings")

    scores = []
    for doc, content, vec in cur.fetchall():
        vec = np.frombuffer(vec, dtype=np.float32)
        score = cosine_sim(q_emb, vec)
        scores.append((score, doc, content))

    conn.close()
    scores.sort(reverse=True, key=lambda x: x[0])
    return scores[:top_k]
