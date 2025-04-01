from fastapi import FastAPI

from pydantic import BaseModel
from typing import Optional
import uvicorn

from backend.view import UserInfo
from agents.agent_conversation_system import AgentConversationSystem
app = FastAPI()

@app.post("/submit")
async def submit_data(request_body: UserInfo):
    
    system = AgentConversationSystem(user_info=request_body)
    system.run_simulation("암보험 가입 상품 추천해줘")
    result = system.get_script()
    
    return {"message": "success", "data": result}

@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}

if __name__=='__main__':
    uvicorn.run(app="main:app", port=8000, reload=True, host='127.0.0.1')