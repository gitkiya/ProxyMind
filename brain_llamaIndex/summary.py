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


def summarize_with_groq(memories):
    combined = "\n".join([f"- {m}" for m in memories])
    prompt = f"""You are maintaining a long-term memory summary for an AI called ProxyMind.
Summarize these memories into a smart, complete profile of the user.

Include ALL of these if present:
- Facts: who they are, what they do, their goals, projects, deadlines
- Decisions: choices they made, directions they took, things they changed
- Progress: what they completed, what they started, where they are now
- Behavioral patterns: how they think, how they work, how they handle challenges
- Emotional context: what stressed them, what excited them, how they responded

Rules:
- Be specific with names, projects, technologies, dates when mentioned
- Write as if briefing someone who has never met this user but needs to know them well
- Preserve details that make this person unique — not generic summaries
- Past deadlines or resolved issues should mention the outcome not the stress
- 3-5 sentences maximum
- Plain sentences only, no bullet points

Memories:
{combined}

User summary:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


def check_and_trigger(user_id):
    """
    Runs on every session start.
    Checks if weekly or monthly summarization is due.
    """
    conn = connect_db()
    cursor = conn.cursor()

    # check last weekly summary timestamp
    cursor.execute("""
        SELECT timestamp FROM proxymind_memories
        WHERE user_id = %s AND memory_type = 'weekly'
        ORDER BY timestamp DESC LIMIT 1
    """, (user_id,))
    last_weekly = cursor.fetchone()

    # check last monthly summary timestamp
    cursor.execute("""
        SELECT timestamp FROM proxymind_memories
        WHERE user_id = %s AND memory_type = 'monthly'
        ORDER BY timestamp DESC LIMIT 1
    """, (user_id,))
    last_monthly = cursor.fetchone()

    cursor.close()
    conn.close()

    now = datetime.now()

    # trigger weekly if 7 days passed or never summarized
    if not last_weekly or (now - last_weekly[0].replace(tzinfo=None)) > timedelta(days=7):
        print("[Summarizer] Weekly summarization triggered")
        weekly_summarize(user_id)

    # trigger monthly if 30 days passed or never summarized
    if not last_monthly or (now - last_monthly[0].replace(tzinfo=None)) > timedelta(days=30):
        print("[Summarizer] Monthly summarization triggered")
        monthly_summarize(user_id)


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
    noise_rows = cursor.fetchall()

    # promote uncertain with retrieval_count > 0 → core
    cursor.execute("""
        UPDATE proxymind_memories
        SET memory_type = 'core'
        WHERE user_id = %s
        AND memory_type = 'uncertain'
        AND retrieval_count > 0
    """, (user_id,))
    promoted = cursor.rowcount
    print(f"[Summarizer] Promoted {promoted} uncertain memories to core")

    # delete uncertain never retrieved
    cursor.execute("""
        DELETE FROM proxymind_memories
        WHERE user_id = %s
        AND memory_type = 'uncertain'
        AND retrieval_count = 0
    """, (user_id,))
    deleted_uncertain = cursor.rowcount
    print(f"[Summarizer] Deleted {deleted_uncertain} uncertain memories never retrieved")

    if noise_rows:
        ids = [r[0] for r in noise_rows]
        contents = [r[1] for r in noise_rows]

        print(f"[Summarizer] Compressing {len(noise_rows)} noise memories...")
        summary = summarize_with_groq(contents)
        embedding = model.encode(summary).tolist()

        cursor.execute("""
            INSERT INTO proxymind_memories
            (user_id, session_id, content, embedding, memory_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, "weekly_summary", summary, embedding, "weekly"))

        cursor.execute("""
            DELETE FROM proxymind_memories
            WHERE id = ANY(%s)
        """, (ids,))

        print(f"[Summarizer] Weekly summary stored. Noise deleted.")
    else:
        print("[Summarizer] No noise memories to compress this week.")

    conn.commit()
    cursor.close()
    conn.close()


def monthly_summarize(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    # fetch all weekly summaries + core memories
    cursor.execute("""
        SELECT id, content FROM proxymind_memories
        WHERE user_id = %s
        AND memory_type IN ('weekly', 'core')
    """, (user_id,))
    rows = cursor.fetchall()

    if not rows:
        print("[Summarizer] No memories to compress into monthly summary.")
        conn.close()
        return

    ids = [r[0] for r in rows]
    contents = [r[1] for r in rows]

    print(f"[Summarizer] Compressing {len(rows)} memories into monthly summary...")
    summary = summarize_with_groq(contents)
    embedding = model.encode(summary).tolist()

    cursor.execute("""
        INSERT INTO proxymind_memories
        (user_id, session_id, content, embedding, memory_type)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, "monthly_summary", summary, embedding, "monthly"))

    cursor.execute("""
        DELETE FROM proxymind_memories
        WHERE id = ANY(%s)
    """, (ids,))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"[Summarizer] Monthly summary stored. Weekly and core compressed.")


# test
if __name__ == "__main__":
    check_and_trigger(user_id="user_1")