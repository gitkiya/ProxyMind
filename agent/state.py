from typing import TypedDict, List, Optional

class ProxyMindState(TypedDict):
    # user info
    user_id: str
    session_id: str
    
    # conversation
    message: str
    
    # memory retrieval
    topic: Optional[str]
    memories: Optional[List[str]]
    
    # response building
    context: Optional[str]
    response: Optional[str]