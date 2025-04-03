from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
from agents.custom_agents import SalesAgent, TechnicalAgent, CustomerServiceAgent, HumanProxy

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 에이전트 초기화
sales_agent = SalesAgent()
technical_agent = TechnicalAgent()
customer_service_agent = CustomerServiceAgent()
human_proxy = HumanProxy()

class ChatMessage(BaseModel):
    message: str
    agent_type: str = "sales"  # "sales", "technical", "customer_service"
    conversation_history: List[Dict] = []

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    try:
        # 에이전트 선택
        agent = {
            "sales": sales_agent,
            "technical": technical_agent,
            "customer_service": customer_service_agent
        }.get(chat_message.agent_type, sales_agent)
        
        # 대화 기록 설정
        agent.conversation_history = chat_message.conversation_history
        
        # 응답 생성
        response = agent.generate_reply(
            messages=[{"content": chat_message.message, "role": "user"}]
        )
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 