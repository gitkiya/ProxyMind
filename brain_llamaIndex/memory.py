import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sentence_transformers import SentenceTransformer
from connect_db import connect_db
from brain_llamaIndex.classifier import classify_memory

model = SentenceTransformer("all-MiniLM-L6-v2")

def store_memory(user_id, session_id, content):
    # classify first
    memory_type = classify_memory(content)
    print(f"Classified as: {memory_type.upper()}")

    # noise → discard immediately, never store
    if memory_type == "noise":
        print(f"Noise discarded — not stored: {content}")
        return

    # core and uncertain → store
    embedding = model.encode(content).tolist()

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO proxymind_memories
        (user_id, session_id, content, embedding, memory_type)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, session_id, content, embedding, memory_type)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Memory stored as {memory_type.upper()}: {content}")

# test it
if __name__ == "__main__":
    test_cases = [
        "I finished integrating FastAPI with LangGraph today",
        "what time is it",
        "building something with Mani for YC application",
        "okay sure",
        "I was stressed about the July deadline but feeling better now",
    ]

    for content in test_cases:
        print(f"\nInput: {content}")
        store_memory("user_1", "session_test", content)
        print("---")