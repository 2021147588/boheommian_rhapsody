import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import inspect
import os
from dotenv import load_dotenv
from agents.planner_agent.router_agent import RouterAgent
from agents.planner_agent.sales_agent import SalesAgent
from agents.planner_agent.rag_agent import RAGAgent
from autogen import Agent

load_dotenv()

class AgentResponse(BaseModel):
    current_agent: Any
    messages: List[Dict[str, Any]]

class Orchestrator:
    def __init__(self):
        # 시작 에이전트를 라우터로 설정
        self.router_agent = RouterAgent()
        self.sales_agent = SalesAgent()
        self.rag_agent = RAGAgent()
        
        self.current_agent = self.router_agent.get_agent()
        self.messages = []
        
    def handle_message(self, user_message: str) -> str:
        """사용자 메시지를 처리하고 응답을 반환합니다."""
        self.messages.append({"role": "user", "content": user_message})
        
        # 에이전트 응답 처리
        response = self._process_agent_response()
        
        # 마지막 응답 메시지 반환
        for msg in reversed(self.messages):
            if msg["role"] == "assistant" and msg.get("content"):
                return msg["content"]
        
        return "응답을 생성하는 데 문제가 발생했습니다."
    
    def _process_agent_response(self) -> AgentResponse:
        """현재 에이전트의 응답을 처리하고 핸드오프 여부를 확인합니다."""
        # 에이전트에게 메시지 전달
        response = self.current_agent.generate_reply(self.messages)
        
        # 응답 메시지 추가
        if isinstance(response, dict) and "content" in response:
            self.messages.append(response)
            
            # 핸드오프 처리
            if "function_call" in response:
                function_call = response["function_call"]
                if isinstance(function_call, dict) and "name" in function_call:
                    # 핸드오프 함수 호출
                    if function_call["name"] == "transfer_to_sales_agent":
                        print("핸드오프: 영업 에이전트로 전환")
                        self.current_agent = self.sales_agent.get_agent()
                    elif function_call["name"] == "transfer_to_rag_agent":
                        print("핸드오프: RAG 에이전트로 전환")
                        self.current_agent = self.rag_agent.get_agent()
                    
                    # 핸드오프 결과 메시지 추가
                    self.messages.append({
                        "role": "system",
                        "content": f"에이전트가 {self.current_agent.name}(으)로 전환되었습니다."
                    })
                    
                    # 새 에이전트에게 다시 처리 요청
                    return self._process_agent_response()
        
        return AgentResponse(current_agent=self.current_agent, messages=self.messages)
    
    def reset(self):
        """대화를 초기화하고 라우터 에이전트로 돌아갑니다."""
        self.current_agent = self.router_agent.get_agent()
        self.messages = []

# 예제 사용법
if __name__ == "__main__":
    orchestrator = Orchestrator()
    
    # 대화 예시
    responses = [
        orchestrator.handle_message("보험 상품 중에 암보험에 대해 알려주세요."),
        orchestrator.handle_message("제게 맞는 상품을 추천해주세요."),
        orchestrator.handle_message("이 상품의 보장 내용이 궁금합니다.")
    ]
    
    for i, response in enumerate(responses, 1):
        print(f"응답 {i}: {response}") 