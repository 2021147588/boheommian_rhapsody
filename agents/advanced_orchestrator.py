import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from agents.advanced_agents.router_agent import AdvancedRouterAgent
from agents.advanced_agents.sales_agent import AdvancedSalesAgent
from agents.advanced_agents.rag_agent import AdvancedRAGAgent
from agents.advanced_agents.recommendation_agent import AdvancedRecommendationAgent

load_dotenv()

class AdvancedOrchestrator:
    def __init__(self):
        """에이전트 시스템 초기화"""
        self.router_agent = AdvancedRouterAgent()
        self.sales_agent = AdvancedSalesAgent()
        self.rag_agent = AdvancedRAGAgent()
        self.recommendation_agent = AdvancedRecommendationAgent()
        self.current_agent = self.router_agent
        self.messages = []
        self.conversation_history = []
        self.active_agent = None
        self.active_agent_name = None
        print(f"[System] 오케스트레이터 초기화 - 시작 에이전트: {self.current_agent.name}")
    
    def process_message(self, message: str) -> str:
        """
        사용자 메시지를 처리하고 적절한 에이전트로 라우팅합니다.
        
        Args:
            message (str): 사용자 메시지
            
        Returns:
            str: 에이전트 응답
        """
        print(f"[AdvancedOrchestrator] Processing message: {message}")
        
        # 메시지 목록에 사용자 메시지 추가
        self.messages.append({"role": "user", "content": message})
        
        # 현재 활성 에이전트 확인
        if self.active_agent_name is None:
            # 첫 메시지는 라우터 에이전트로 전달
            self.active_agent = self.router_agent
            self.active_agent_name = "router"
            print(f"[AdvancedOrchestrator] Initial router agent setup")
        
        # 에이전트에 메시지 전달 - run_interaction 사용
        response = self.active_agent.run_interaction(self.messages)
        
        # 에이전트 응답 추출
        agent_response = ""
        for msg in reversed(response.messages):
            if msg.get("role") == "assistant" and msg.get("content"):
                agent_response = msg.get("content")
                break
            
        print(f"[AdvancedOrchestrator] Agent response: {agent_response}")
        
        # 핸드오프 신호 확인
        handoff_signal = None
        
        # 핸드오프 확인 로직
        if "HANDOFF_TO_SALES_AGENT" in agent_response:
            handoff_signal = "sales"
            agent_response = agent_response.replace("HANDOFF_TO_SALES_AGENT", "")
        elif "HANDOFF_TO_RAG_AGENT" in agent_response:
            handoff_signal = "rag"
            agent_response = agent_response.replace("HANDOFF_TO_RAG_AGENT", "")
        elif "HANDOFF_TO_RECOMMENDATION_AGENT" in agent_response:
            handoff_signal = "recommendation"
            agent_response = agent_response.replace("HANDOFF_TO_RECOMMENDATION_AGENT", "")
        
        # 핸드오프 처리
        if handoff_signal:
            source_agent = self.active_agent
            source_agent_name = self.active_agent_name
            
            if handoff_signal == "sales":
                self.active_agent = self.sales_agent
                self.active_agent_name = "sales"
                print(f"[AdvancedOrchestrator] Handoff from {source_agent_name} to sales agent")
            elif handoff_signal == "rag":
                self.active_agent = self.rag_agent
                self.active_agent_name = "rag"
                print(f"[AdvancedOrchestrator] Handoff from {source_agent_name} to RAG agent")
            elif handoff_signal == "recommendation":
                self.active_agent = self.recommendation_agent
                self.active_agent_name = "recommendation"
                print(f"[AdvancedOrchestrator] Handoff from {source_agent_name} to recommendation agent")
            
            # 프로필 정보 전달
            self._transfer_profile_data(source_agent, self.active_agent)
        
        return agent_response
    
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
    
    def _transfer_conversation_history(self, source_agent, target_agent):
        """
        소스 에이전트에서 타겟 에이전트로 대화 이력을 전달합니다.
        
        Args:
            source_agent: 소스 에이전트
            target_agent: 타겟 에이전트
        """
        try:
            # 메시지 목록 복사
            if hasattr(source_agent, 'messages') and source_agent.messages:
                if hasattr(target_agent, 'messages'):
                    target_agent.messages = source_agent.messages.copy()
            
            # 대화 이력 복사
            if hasattr(source_agent, 'conversation_history') and source_agent.conversation_history:
                if hasattr(target_agent, 'conversation_history'):
                    target_agent.conversation_history = source_agent.conversation_history.copy()
            
            print(f"[ConversationHistoryTransfer] Conversation history transferred successfully")
        except Exception as e:
            print(f"[ConversationHistoryTransfer] Error transferring conversation history: {e}")
    
    def reset(self):
        """대화 상태를 초기화하고 라우터 에이전트로 돌아갑니다."""
        old_agent = self.current_agent
        self.current_agent = self.router_agent
        self.messages = []
        self.conversation_history = []
        self.active_agent = None
        self.active_agent_name = None
        print(f"[System] 대화 초기화 완료. 에이전트 재설정: {old_agent.name} -> {self.router_agent.name}")
        return "대화가 초기화되었습니다."
    
    def get_conversation_history(self) -> List[str]:
        """현재까지의 대화 기록을 반환합니다."""
        return self.conversation_history

    def run_with_history(self, chat_history: str, user_message: str) -> str:
        """
        대화 이력을 기반으로 에이전트의 응답을 생성합니다.
        """
        # 수동 대화 로그 삽입
        self.messages = []  # 새 세션처럼 처리
        self.conversation_history = chat_history.split("\n") if chat_history else []

        print(f"[System] 대화 기록과 함께 메시지 처리 시작")
        return self.process_message(user_message)

# 사용 예시
if __name__ == "__main__":
    orchestrator = AdvancedOrchestrator()
    
    print("=== 보험 상담 AI 시스템 ===")
    print("시스템: 안녕하세요! 보험 관련 질문이나 상담이 필요하신가요?")
    print("(종료하려면 'exit' 또는 '종료'를 입력하세요)")
    
    while True:
        user_input = input("\n사용자: ")
        
        if user_input.lower() in ["exit", "종료"]:
            print("시스템: 상담을 종료합니다. 감사합니다!")
            break
        
        if user_input.lower() in ["reset", "초기화"]:
            print(f"시스템: {orchestrator.reset()}")
            continue
        
        response = orchestrator.process_message(user_input)
        print(f"\n에이전트: {response}") 