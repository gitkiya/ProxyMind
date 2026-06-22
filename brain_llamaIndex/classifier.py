import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_memory(content):
    content_lower = content.lower().strip()

    # ─────────────────────────────
    # STAGE 1 — Rule based filter
    # fast, no API call needed
    # ─────────────────────────────

    # definite noise — questions
    question_starters = [
        "what", "how", "why", "when", "where", "who",
        "can", "do", "did", "is", "are", "should",
        "would", "could", "will", "have", "has"
    ]
    if any(content_lower.startswith(w) for w in question_starters):
        return "noise"

    # definite noise — too short
    if len(content.split()) < 4:
        return "noise"

    # definite noise — filler words
    fillers = [
        "okay", "ok", "sure", "thanks", "thank you",
        "lol", "haha", "hi", "hello", "bye", "yeah",
        "yep", "nope", "cool", "nice", "great", "awesome"
    ]
    if content_lower.strip("!?.") in fillers:
        return "noise"

    # definite core — strong signals
    core_signals = [
        "i am", "i'm", "i have", "i've", "i finished",
        "i built", "i decided", "i learned", "i completed",
        "i'm building", "i was", "i feel", "i need",
        "i want", "i started", "i deployed", "i fixed",
        "frustrated", "excited", "stressed", "proud",
        "confused", "motivated", "worried", "happy",
        "deadline", "august", "proxymind", "langgraph",
        "fastapi", "pgvector", "supabase", "phase",
        "internship", "scholarship", "university", "exam"
    ]
    if any(signal in content_lower for signal in core_signals):
        return "core"

    # ─────────────────────────────
    # STAGE 2 — LLM for ambiguous
    # only reaches here if neither
    # obviously core nor noise
    # ─────────────────────────────
    prompt = f"""You are a memory classifier for ProxyMind.
This memory passed basic filters and needs careful judgment.

Classify as:
- "core" if it reveals something meaningful about the user
  (who they are, what they're building, how they feel, decisions made)
- "noise" if it has no lasting informational value
- "uncertain" if genuinely unclear but MIGHT be important

Respond with ONE word only: core, noise, or uncertain

Memory: "{content}"
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=5,
        temperature=0
    )

    result = response.choices[0].message.content.strip().lower()

    if "core" in result:
        return "core"
    elif "uncertain" in result:
        return "uncertain"
    else:
        return "noise"


# test it
if __name__ == "__main__":
    test_memories = [
        "what do u think about yourself?",
        "I finished building the LangGraph agent today",
        "how does cosine similarity work?",
        "I am building ProxyMind for my scholarship application",
        "okay cool",
        "I was frustrated when the classifier stored noise memories",
        "can you explain HNSW?",
        "I decided to use Supabase instead of local PostgreSQL",
        "what time is it",
        "I have a deployment deadline of August 1 2026",
        "building something interesting here",
        "the system works better now",
    ]

    print("Testing two-stage classifier...\n")
    for memory in test_memories:
        result = classify_memory(memory)
        print(f"{result.upper():<12} → {memory}")