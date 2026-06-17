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

    return results
    
        

# # test it
# retrieve_memories(
#     query="what am I building",
#     user_id="user_1"
# )