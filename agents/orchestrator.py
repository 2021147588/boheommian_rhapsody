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

    def process_message(self, message: str) -> str:
        """
        사용자 메시지를 처리하고 적절한 에이전트로 라우팅합니다.
        
        Args:
            message (str): 사용자 메시지
            
        Returns:
            str: 에이전트 응답
        """
        print(f"Processing message: {message}")
        
        # 현재 활성 에이전트 확인
        if self.active_agent_name is None:
            # 첫 메시지는 라우터 에이전트로 전달
            self.active_agent = self.router_agent
            self.active_agent_name = "router"
            print(f"Initial router agent setup")
        
        # 에이전트에 메시지 전달
        response = self.active_agent.run(message)
        print(f"Agent response: {response}")
        
        # 핸드오프 신호 확인
        handoff_signal = None
        
        # 라우터 -> 다른 에이전트 전환
        if self.active_agent_name == "router":
            if "HANDOFF_TO_SALES_AGENT" in response:
                handoff_signal = "sales"
                response = response.replace("HANDOFF_TO_SALES_AGENT", "")
            elif "HANDOFF_TO_RAG_AGENT" in response:
                handoff_signal = "rag"
                response = response.replace("HANDOFF_TO_RAG_AGENT", "")
            elif "HANDOFF_TO_RECOMMENDATION_AGENT" in response:
                handoff_signal = "recommendation"
                response = response.replace("HANDOFF_TO_RECOMMENDATION_AGENT", "")
        
        # 추천 에이전트 -> 영업 에이전트 전환
        elif self.active_agent_name == "recommendation":
            if "HANDOFF_TO_SALES_AGENT" in response:
                handoff_signal = "sales"
                response = response.replace("HANDOFF_TO_SALES_AGENT", "")
            elif "HANDOFF_TO_RAG_AGENT" in response:
                handoff_signal = "rag"
                response = response.replace("HANDOFF_TO_RAG_AGENT", "")
        
        # 영업 에이전트 -> 추천/RAG 에이전트 전환
        elif self.active_agent_name == "sales":
            if "HANDOFF_TO_RECOMMENDATION_AGENT" in response:
                handoff_signal = "recommendation"
                response = response.replace("HANDOFF_TO_RECOMMENDATION_AGENT", "")
            elif "HANDOFF_TO_RAG_AGENT" in response:
                handoff_signal = "rag"
                response = response.replace("HANDOFF_TO_RAG_AGENT", "")
        
        # RAG 에이전트 -> 다른 에이전트 전환
        elif self.active_agent_name == "rag":
            if "HANDOFF_TO_SALES_AGENT" in response:
                handoff_signal = "sales"
                response = response.replace("HANDOFF_TO_SALES_AGENT", "")
            elif "HANDOFF_TO_RECOMMENDATION_AGENT" in response:
                handoff_signal = "recommendation"
                response = response.replace("HANDOFF_TO_RECOMMENDATION_AGENT", "")
        
        # 핸드오프 처리
        if handoff_signal:
            source_agent = self.active_agent
            source_agent_name = self.active_agent_name
            
            if handoff_signal == "sales":
                self.active_agent = self.sales_agent
                self.active_agent_name = "sales"
                print(f"Handoff from {source_agent_name} to sales agent")
            elif handoff_signal == "rag":
                self.active_agent = self.rag_agent
                self.active_agent_name = "rag"
                print(f"Handoff from {source_agent_name} to RAG agent")
            elif handoff_signal == "recommendation":
                self.active_agent = self.recommendation_agent
                self.active_agent_name = "recommendation"
                print(f"Handoff from {source_agent_name} to recommendation agent")
                
            # 대화 이력 및 컨텍스트 전달
            self._transfer_conversation_history(source_agent, self.active_agent)
        
        return response

    def _transfer_conversation_history(self, source_agent, target_agent):
        """
        소스 에이전트에서 타겟 에이전트로 대화 이력 및 컨텍스트를 전달합니다.
        
        Args:
            source_agent: 소스 에이전트
            target_agent: 타겟 에이전트
        """
        try:
            # 대화 이력 복사
            target_agent.conversation_history = source_agent.conversation_history.copy()
            
            # 컨텍스트 복사
            target_agent.context = source_agent.context.copy()
            
            print(f"[ConversationHistoryTransfer] Conversation history transferred successfully")
        except Exception as e:
            print(f"[ConversationHistoryTransfer] Error transferring conversation history: {e}")

    def _transfer_profile_data(self, source_agent, target_agent):
        """
        소스 에이전트에서 타겟 에이전트로 고객 프로필 정보를 전달합니다.
        
        Args:
            source_agent: 소스 에이전트
            target_agent: 타겟 에이전트
        """
        try:
            # 고객 프로필이 있는 에이전트인지 확인
            if hasattr(source_agent, 'customer_profile') and source_agent.customer_profile:
                if hasattr(target_agent, 'customer_profile'):
                    
                    # 프로필 데이터 복사
                    source_profile = source_agent.customer_profile
                    
                    # JSON으로 변환하여 전달
                    if hasattr(source_profile, 'to_dict'):
                        profile_data = source_profile.to_dict()
                        
                        # 타겟 에이전트 프로필 업데이트
                        for category, fields in profile_data.items():
                            for field, value in fields.items():
                                if hasattr(target_agent.customer_profile, field):
                                    setattr(target_agent.customer_profile, field, value)
                        
                        print(f"[ProfileTransfer] Profile data transferred successfully")
                    else:
                        print(f"[ProfileTransfer] Source profile doesn't have to_dict method")
                else:
                    print(f"[ProfileTransfer] Target agent doesn't have customer_profile")
        except Exception as e:
            print(f"[ProfileTransfer] Error transferring profile data: {e}")

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