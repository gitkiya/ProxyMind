import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from groq import Groq
from dotenv import load_dotenv
from connect_db import connect_db
from sentence_transformers import SentenceTransformer
from datetime import datetime, timedelta

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = SentenceTransformer("all-MiniLM-L6-v2")

def summarize_with_groq(memories, summary_type):
    combined = "\n".join([f"- {m}" for m in memories])
    prompt = f"""You are summarizing memories for an AI called ProxyMind.
Write a brief 2-3 sentence summary capturing the most important context.
Plain sentences only. No bullet points.

Memories:
{combined}

Summary:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def weekly_summarize(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    # fetch noise memories from this week
    cursor.execute("""
        SELECT id, content FROM proxymind_memories
        WHERE user_id = %s
        AND memory_type = 'noise'
        AND timestamp >= %s
    """, (user_id, week_start))

    rows = cursor.fetchall()

    if not rows:
        print("No noise memories to summarize.")
        conn.close()
        return

    ids = [r[0] for r in rows]
    contents = [r[1] for r in rows]

    print(f"Compressing {len(rows)} noise memories into weekly summary...")

    summary = summarize_with_groq(contents, "weekly")
    embedding = model.encode(summary).tolist()

    # store weekly summary
    cursor.execute("""
        INSERT INTO proxymind_memories
        (user_id, session_id, content, embedding, memory_type)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, "weekly_summary", summary, embedding, "weekly"))

    # delete raw noise
    cursor.execute("""
        DELETE FROM proxymind_memories
        WHERE id = ANY(%s)
    """, (ids,))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Weekly summary stored. Raw noise deleted.")
    print(f"Summary: {summary}")

def monthly_summarize(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    # fetch all weekly summaries + core memories
    cursor.execute("""
        SELECT id, content, memory_type FROM proxymind_memories
        WHERE user_id = %s
        AND memory_type IN ('weekly', 'core')
    """, (user_id,))

    rows = cursor.fetchall()

    if not rows:
        print("No memories to compress into monthly summary.")
        conn.close()
        return

    ids = [r[0] for r in rows]
    contents = [r[1] for r in rows]

    print(f"Compressing {len(rows)} memories into monthly summary...")

    summary = summarize_with_groq(contents, "monthly")
    embedding = model.encode(summary).tolist()

    # store monthly summary
    cursor.execute("""
        INSERT INTO proxymind_memories
        (user_id, session_id, content, embedding, memory_type)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, "monthly_summary", summary, embedding, "monthly"))

    # delete weekly and core raw
    cursor.execute("""
        DELETE FROM proxymind_memories
        WHERE id = ANY(%s)
    """, (ids,))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Monthly summary stored. Weekly and core memories compressed and deleted.")
    print(f"Summary: {summary}")

# # test weekly
# print("=== WEEKLY SUMMARIZER ===")
# weekly_summarize(user_id="user_1")