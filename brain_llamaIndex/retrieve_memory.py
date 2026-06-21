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

    # fetch top N memories by cosine similarity
    cursor.execute(
    """
    SELECT id, content, memory_type, timestamp,
    1 - (embedding <=> %s::vector) AS similarity
    FROM proxymind_memories
    WHERE user_id = %s
    AND 1 - (embedding <=> %s::vector) > 0.15
    ORDER BY similarity DESC
    LIMIT %s
    """,
    (query_embedding, user_id, query_embedding, top_n)
    )
    
    results = cursor.fetchall()

    # increment retrieval_count for each retrieved memory
    if results:
        retrieved_ids = [row[0] for row in results]
        cursor.execute(
            """
            UPDATE proxymind_memories
            SET retrieval_count = retrieval_count + 1
            WHERE id = ANY(%s)
            """,
            (retrieved_ids,)
        )
        conn.commit()

    cursor.close()
    conn.close()

    return results
    
        

# test it
retrieve_memories(
    query="what am I building",
    user_id="user_1"
)