import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_memory(content):
    prompt = f"""You are a memory classifier for an AI system called ProxyMind.
Classify this memory as either "core" or "noise".

core  → facts about the user, decisions made, goals,
        achievements, emotional state (frustrated, excited,
        stressed, proud, confused)
noise → small talk, filler phrases, repetitive questions
        with no new information

Respond with ONE word only: core or noise

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
    elif "noise" in result:
        return "noise"
    else:
        return "noise"  # default to noise if unclear

# # test it
# test_memories = [
#     "I am building an AI called ProxyMind that remembers users across 7 days",
#     "how's my progress?",
#     "I was really frustrated when pgvector wouldn't install",
#     "what time is it",
#     "I decided to use fixed weekly blocks instead of rolling window",
#     "haha yeah",
# ]

# print("Testing classifier...\n")
# for memory in test_memories:
#     result = classify_memory(memory)
#     print(f"{result.upper()} → {memory}")