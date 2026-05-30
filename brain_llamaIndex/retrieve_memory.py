import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sentence_transformers import SentenceTransformer
from connect_db import connect_db

model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_memories(query, user_id, top_n=3):
    query_embedding = model.encode(query).tolist()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT content, memory_type, timestamp,
        1 - (embedding <=> %s::vector) AS similarity
        FROM proxymind_memories
        WHERE user_id = %s
        ORDER BY similarity DESC
        LIMIT %s
        """,
        (query_embedding, user_id, top_n)
    )

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    print(f"\nTop {top_n} memories for: '{query}'\n")
    for row in results:
        print(f"memory   : {row[0]}")
        print(f"type     : {row[1]}")
        print(f"stored   : {row[2]}")
        print(f"similarity: {round(row[3], 4)}")
        print("---")

# test it
retrieve_memories(
    query="what am I building",
    user_id="user_1"
)