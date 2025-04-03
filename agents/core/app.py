"""
에이전트 시스템 메인 애플리케이션 - 시스템 초기화 및 구성

이 모듈은 모든 에이전트를 설정하고 오케스트레이터와 연결하며,
시스템과 상호작용하기 위한 간단한 인터페이스를 제공합니다.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv

from agents.core.orchestrator import Orchestrator
from agents.core.profile_agent import ProfileAgent
from agents.core.sales_agent import SalesAgent
from agents.core.general_agent import GeneralAgent
from agents.core.router_agent import RouterAgent
from agents.core.rag_agent import RAGEngine

# 환경 변수 로드
load_dotenv()

class AgentApp:
    """
    에이전트 시스템의 메인 애플리케이션 클래스.
    
    이 클래스는 모든 에이전트를 초기화하고, 오케스트레이터를 구성하며,
    에이전트 시스템과 상호작용하기 위한 메소드를 제공합니다.
    """
    
    def __init__(self):
        """에이전트 애플리케이션 초기화."""
        self._initialize_agents()
        self.orchestrator = Orchestrator()
        self.rag_engine = RAGEngine()  # RAG 엔진 초기화
        print("멀티 에이전트 시스템 초기화 완료")
    
    def _initialize_agents(self):
        """모든 에이전트 초기화 및 등록."""
        # 에이전트 초기화 - 자동으로 등록됨
        self.router_agent = RouterAgent()
        self.profile_agent = ProfileAgent()
        self.sales_agent = SalesAgent()
        self.general_agent = GeneralAgent()
        
        agent_names = [self.router_agent.name, self.profile_agent.name, 
                       self.sales_agent.name, self.general_agent.name]
        print(f"초기화된 에이전트: {', '.join(agent_names)}")
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        사용자 메시지를 처리하고 응답을 생성합니다.
        
        이 메소드는 메시지 내용에 기반하여 적절한 에이전트로
        메시지를 라우팅하는 작업을 처리합니다.
        
        인자:
            message: 처리할 사용자 메시지
            
        반환값:
            응답과 메타데이터를 포함하는 딕셔너리
        """
        # 먼저 어떤 에이전트가 메시지를 처리해야 하는지와 RAG 사용 여부 결정
        agent_name, use_rag = await self.router_agent.determine_agent(message)
        
        # 메시지를 기반으로 프로필 업데이트
        profile_summary = await self.profile_agent.update_profile(
            self.orchestrator.conversation_history + [{"role": "user", "content": message}]
        )
        
        # 대화 기록에 프로필 요약 추가
        if profile_summary:
            self.orchestrator.conversation_history.append({
                "role": "system",
                "content": f"profile_info: {profile_summary}"
            })
        
        # 오케스트레이터로 메시지 처리 (RAG 플래그 포함)
        response_data = await self.orchestrator.process_message(message, agent_name, use_rag)
        
        # 필요한 추가 메타데이터 추가
        response_data["profile_summary"] = profile_summary
        response_data["use_rag"] = use_rag
        
        return response_data
    
    async def get_next_questions(self, use_rag: bool = False) -> str:
        """
        현재 프로필을 기반으로 다음 질문 제안을 생성합니다.
        
        인자:
            use_rag: RAG 기능 사용 여부
            
        반환값:
            제안된 질문을 포함하는 문자열
        """
        # 현재 프로필을 딕셔너리로 가져오기
        profile_dict = self.profile_agent.get_profile_as_dict()
        
        # JSON 문자열로 변환
        profile_json = json.dumps(profile_dict, ensure_ascii=False)
        
        # RAG 플래그 설정
        self.sales_agent.use_rag = use_rag
        
        # 프로필을 기반으로 질문 생성
        return await self.sales_agent.generate_next_questions(profile_json)
    
    async def get_recommendation(self, use_rag: bool = True) -> str:
        """
        현재 프로필을 기반으로 상품 추천을 생성합니다.
        
        인자:
            use_rag: RAG 기능 사용 여부 (기본적으로 사용)
            
        반환값:
            상품 추천을 포함하는 문자열
        """
        # 현재 프로필을 딕셔너리로 가져오기
        profile_dict = self.profile_agent.get_profile_as_dict()
        
        # JSON 문자열로 변환
        profile_json = json.dumps(profile_dict, ensure_ascii=False)
        
        # RAG 플래그 설정
        self.sales_agent.use_rag = use_rag
        
        # 프로필을 기반으로 추천 생성
        return await self.sales_agent.generate_recommendation(profile_json)
    
    async def analyze_query_for_rag(self, message: str) -> Tuple[bool, float]:
        """
        메시지가 RAG를 필요로 하는지 분석합니다.
        
        인자:
            message: 분석할 사용자 메시지
            
        반환값:
            RAG 필요 여부와 신뢰도를 포함하는 튜플
        """
        return await self.rag_engine.is_rag_needed(message)
    
    def get_profile_summary(self) -> str:
        """
        현재 사용자 프로필 요약을 가져옵니다.
        
        반환값:
            사용자 프로필을 요약한 문자열
        """
        return self.profile_agent.get_profile_summary()
    
    def reset_conversation(self) -> None:
        """대화 기록 및 프로필을 초기화합니다."""
        self.orchestrator.reset_conversation()
        self.profile_agent.reset_profile()
        print("대화 및 프로필이 초기화되었습니다")
    
    def get_current_agent(self) -> str:
        """
        현재 활성화된 에이전트의 이름을 가져옵니다.
        
        반환값:
            현재 에이전트의 이름
        """
        return self.orchestrator.current_agent_name or "선택된 에이전트 없음"


# 싱글톤 인스턴스
_app_instance = None

def get_app() -> AgentApp:
    """
    싱글톤 애플리케이션 인스턴스를 가져옵니다.
    
    반환값:
        AgentApp 인스턴스
    """
    global _app_instance
    if _app_instance is None:
        _app_instance = AgentApp()
    return _app_instance 