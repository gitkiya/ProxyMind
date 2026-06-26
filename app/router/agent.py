from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from app.supabase import supabase
from agent.graph import build_graph
from brain_llamaIndex.summary import check_and_trigger

router = APIRouter(prefix="/proxymind", tags=["ProxyMind"])

class MessageRequest(BaseModel):
    message: str
    session_id: str

def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        user = supabase.auth.get_user(token)
        return user.user.id
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/chat")
def chat(request: MessageRequest, user_id: str = Depends(get_current_user)):
    # check if weekly/monthly summarization is due
    check_and_trigger(user_id)

    # run the agent
    agent = build_graph()

    result = agent.invoke({
        "user_id": user_id,
        "session_id": request.session_id,
        "message": request.message,
        "topic": None,
        "memories": None,
        "context": None,
        "response": None
    })

    return {
        "response": result["response"],
        "user_id": user_id,
        "session_id": request.session_id
    }