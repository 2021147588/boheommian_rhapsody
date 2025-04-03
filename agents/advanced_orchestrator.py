import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from agents.advanced_agents.router_agent import AdvancedRouterAgent
from agents.advanced_agents.sales_agent import AdvancedSalesAgent
from agents.advanced_agents.rag_agent import AdvancedRAGAgent

load_dotenv()

class AdvancedOrchestrator:
    def __init__(self):
        """에이전트 시스템 초기화"""
        self.router_agent = AdvancedRouterAgent()
        self.current_agent = self.router_agent
        self.messages = []
        self.conversation_history = []
        print(f"[System] 오케스트레이터 초기화 - 시작 에이전트: {self.current_agent.name}")
    
    def process_message(self, user_message: str) -> str:
        """
        사용자 메시지를 처리하고 에이전트 응답을 반환합니다.
        
        Args:
            user_message: 사용자 입력 메시지
            
        Returns:
            에이전트 응답 메시지
        """
        # 사용자 메시지 추가
        self.messages.append({"role": "user", "content": user_message})
        self.conversation_history.append(f"User: {user_message}")
        print(f"[System] 현재 에이전트 ({self.current_agent.name})에게 사용자 메시지 전송 중...")
        
        # 에이전트와 상호작용
        response = self.current_agent.run_interaction(self.messages)
        
        # 핸드오프 처리
        if response.agent != self.current_agent:
            print(f"[System] 핸드오프 발생: {self.current_agent.name} -> {response.agent.name}")
            print(f"[System] 핸드오프 전 메시지 수: {len(self.messages)}, 새 메시지 수: {len(response.messages)}")
            old_agent = self.current_agent
            self.current_agent = response.agent
            print(f"[System] 에이전트 전환 완료: {old_agent.name} -> {self.current_agent.name}")
        else:
            print(f"[System] 동일 에이전트({self.current_agent.name}) 유지, 핸드오프 없음")
        
        # 새 메시지 추가
        before_count = len(self.messages)
        self.messages.extend(response.messages)
        print(f"[System] 메시지 {len(response.messages)}개 추가됨 (총 {len(self.messages)}개)")
        
        # 에이전트 응답 추출
        agent_response = ""
        for msg in reversed(response.messages):
            if msg.get("role") == "assistant" and msg.get("content"):
                agent_response = msg.get("content")
                self.conversation_history.append(f"{self.current_agent.name}: {agent_response}")
                print(f"[System] {self.current_agent.name}의 최종 응답 (길이: {len(agent_response)})")
                break
        
        return agent_response
    
    def reset(self):
        """대화 상태를 초기화하고 라우터 에이전트로 돌아갑니다."""
        old_agent = self.current_agent
        self.current_agent = self.router_agent
        self.messages = []
        self.conversation_history = []
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