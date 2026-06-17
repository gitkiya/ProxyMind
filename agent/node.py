import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from groq import Groq
from dotenv import load_dotenv
from brain_llamaIndex.memory import store_memory
from brain_llamaIndex.retrieve_memory import retrieve_memories
from agent.state import ProxyMindState

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─────────────────────────────
# NODE 1 — receive message
# ─────────────────────────────
def receive_message(state: ProxyMindState) -> ProxyMindState:
    print(f"\n[Node 1] Message received: {state['message']}")
    return state

# ─────────────────────────────
# NODE 2 — detect topic
# ─────────────────────────────
def detect_topic(state: ProxyMindState) -> ProxyMindState:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""Extract 3-5 keywords that represent the topic of this message.
Respond with keywords only, comma separated, nothing else.

Message: "{state['message']}\""""
        }],
        max_tokens=50,
        temperature=0
    )
    
    topic = response.choices[0].message.content.strip()
    print(f"[Node 2] Topic detected: {topic}")
    return {**state, "topic": topic}

# ─────────────────────────────
# NODE 3 — retrieve memories
# ─────────────────────────────
def retrieve_relevant_memories(state: ProxyMindState) -> ProxyMindState:
    results = retrieve_memories(
        query=state["topic"],
        user_id=state["user_id"],
        top_n=3
    )
    
    memories = [row[0] for row in results] if results else []
    print(f"[Node 3] Retrieved {len(memories)} memories")
    return {**state, "memories": memories}

# ─────────────────────────────
# NODE 4 — build context
# ─────────────────────────────
def build_context(state: ProxyMindState) -> ProxyMindState:
    memories = state.get("memories", [])
    
    if memories:
        memory_text = "\n".join([f"- {m}" for m in memories])
        context = f"""You are ProxyMind, an AI that knows the user personally.

What you remember about this user:
{memory_text}

Respond naturally as if you already know them.
Don't say 'based on our previous conversations' — just know it.
Be casual, warm, direct. Like a smart friend."""
    else:
        context = """You are ProxyMind, an AI assistant.
You are meeting this user for the first time.
Be casual, warm, direct. Like a smart friend."""

    print(f"[Node 4] Context built with {len(memories)} memories")
    return {**state, "context": context}

# ─────────────────────────────
# NODE 5 — generate response
# ─────────────────────────────
def generate_response(state: ProxyMindState) -> ProxyMindState:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": state["context"]},
            {"role": "user", "content": state["message"]}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    reply = response.choices[0].message.content.strip()
    print(f"[Node 5] Response generated")
    return {**state, "response": reply}

# ─────────────────────────────
# NODE 6 — store memory
# ─────────────────────────────
def store_new_memory(state: ProxyMindState) -> ProxyMindState:
    from brain_llamaIndex.classifier import classify_memory
    
    classification = classify_memory(state["message"])
    
    if classification == "core":
        store_memory(
            user_id=state["user_id"],
            session_id=state["session_id"],
            content=state["message"]
        )
        print(f"[Node 6] Core memory stored ✅")
    else:
        print(f"[Node 6] Noise discarded ❌ not stored")
    
    return state