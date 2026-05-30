import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sentence_transformers import SentenceTransformer
from connect_db import connect_db
from classifier import classify_memory

model = SentenceTransformer("all-MiniLM-L6-v2")

def store_memory(user_id, session_id, content):
    # classify first
    memory_type = classify_memory(content)
    print(f"Classified as: {memory_type.upper()}")

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
store_memory(
    user_id="user_1",
    session_id="session_1",
    content="I finished building the importance classifier today"
)