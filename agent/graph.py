import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langgraph.graph import StateGraph, END
from agent.state import ProxyMindState
from agent.node import (
    receive_message,
    detect_topic,
    retrieve_relevant_memories,
    build_context,
    generate_response,
    store_new_memory
)

def build_graph():
    # initialize graph with state
    graph = StateGraph(ProxyMindState)

    # add all nodes
    graph.add_node("receive_message", receive_message)
    graph.add_node("detect_topic", detect_topic)
    graph.add_node("retrieve_memories", retrieve_relevant_memories)
    graph.add_node("build_context", build_context)
    graph.add_node("generate_response", generate_response)
    graph.add_node("store_memory", store_new_memory)

    # connect nodes in order
    graph.add_edge("receive_message", "detect_topic")
    graph.add_edge("detect_topic", "retrieve_memories")
    graph.add_edge("retrieve_memories", "build_context")
    graph.add_edge("build_context", "generate_response")
    graph.add_edge("generate_response", "store_memory")
    graph.add_edge("store_memory", END)

    # set entry point
    graph.set_entry_point("receive_message")

    return graph.compile()


# test it
if __name__ == "__main__":
    agent = build_graph()

    result = agent.invoke({
        "user_id": "user_1",
        "session_id": "session_test",
        "message": "what do u think about yourself? why do u save this as core but not as noise cause this question doesn't really have anything u can learn from it? and also do u think this question is important to be remembered for the future? if not then why do u save it as core memory? ",
        "topic": None,
        "memories": None,
        "context": None,
        "response": None
    })

    print("\n" + "="*50)
    print("PROXYMIND RESPONSE:")
    print("="*50)
    print(result["response"])