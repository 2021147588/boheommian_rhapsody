"""
라우터 에이전트 - 사용자 메시지를 분류하고 적절한 에이전트로 라우팅

이 에이전트는 사용자 메시지를 분석하여 어떤 전문 에이전트가
처리해야 하는지 결정하고, 더 효율적인 대화를 가능하게 합니다.
또한 RAG(Retrieval Augmented Generation) 기능이 필요한지 판단합니다.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from openai import AsyncOpenAI
from dotenv import load_dotenv

from agents.core.agent_base import AgentBase
from agents.core.rag_agent import RAGEngine

# 환경 변수 로드
load_dotenv()

class RouterAgent(AgentBase):
    """
    메시지 분류 및 전문가 에이전트로의 라우팅을 담당하는 에이전트.
    
    이 에이전트는 사용자 메시지를 분석하여 의도를 파악하고
    처리를 위해 적절한 전문 에이전트로 라우팅합니다.
    또한 RAG 기능이 필요한지 판단합니다.
    """
    
    def __init__(self, name: str = "RouterAgent"):
        """
        라우터 에이전트를 초기화합니다.
        
        인자:
            name: 에이전트 이름
        """
        # 라우터 에이전트의 시스템 메시지 정의
        system_message = """당신은 사용자의 질문을 분석하고 적합한 전문 에이전트에게 라우팅하는 역할을 합니다.
            
사용자의 질문을 분석하여 다음 중 하나로 분류하세요:
1. GENERAL - 일반적인 대화나 간단한 질문, 인사, 감사 표현
2. SALES - 보험 상품 문의, 판매, 설명, 가입 절차 등

대답은 분류 결과만 간결하게 (GENERAL, SALES) 중 하나만 반환하세요.

- GENERAL 예시: 안녕하세요, 날씨 어때요?, 고마워요
- SALES 예시: 보험 상품 추천해주세요, 운전자보험 알려주세요, 보험료는 얼마인가요
"""
        
        # 기본 클래스 초기화
        super().__init__(
            name=name,
            system_message=system_message
        )
        
        # OpenAI 클라이언트 초기화
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # RAG 엔진 초기화
        self.rag_engine = RAGEngine()
    
    async def classify_query(self, message: str) -> str:
        """
        사용자 메시지를 분석하고 어떤 에이전트가 처리해야 하는지 결정합니다.
        
        인자:
            message: 분류할 사용자 메시지
            
        반환값:
            메시지를 처리해야 하는 에이전트 유형 (GENERAL, SALES)
        """
        try:
            # 프롬프트 생성
            prompt = f"""
분석할 사용자 메시지: {message}

이 메시지를 다음 중 하나로 분류하세요:
- GENERAL: 일반적인 대화, 인사, 간단한 질문
- SALES: 보험 상품, 보장 내용, 가입 절차, 보험료 관련 질문

분류 결과만 대문자로 반환하세요 (GENERAL 또는 SALES).
"""
            
            # OpenAI API 호출
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 응답 추출 및 검증
            result = response.choices[0].message.content.strip().upper()
            
            # 응답 검증
            if result not in ["GENERAL", "SALES"]:
                print(f"[RouterAgent] Invalid classification result: {result}, defaulting to GENERAL")
                return "GENERAL"
                
            return result
            
        except Exception as e:
            print(f"[RouterAgent] Error during classification: {str(e)}")
            # 오류 발생 시 GENERAL로 기본 설정
            return "GENERAL"
    
    async def is_rag_needed(self, message: str) -> Tuple[bool, float]:
        """
        메시지에 RAG(지식 검색) 기능이 필요한지 분석합니다.
        
        인자:
            message: 사용자 메시지
            
        반환값:
            RAG 필요 여부와 신뢰도 점수를 포함하는 튜플
        """
        return await self.rag_engine.is_rag_needed(message)
            
    async def determine_agent(self, message: str) -> Tuple[str, bool]:
        """
        특정 메시지를 처리할 에이전트와 RAG 필요 여부를 결정합니다.
        
        인자:
            message: 사용자 메시지
            
        반환값:
            에이전트 이름과 RAG 플래그를 포함하는 튜플
        """
        # 메시지 분류
        classification = await self.classify_query(message)
        
        # RAG 필요 여부 결정
        rag_needed, confidence = await self.is_rag_needed(message)
        
        # GENERAL 에이전트는 RAG를 사용하지 않음
        if classification == "GENERAL":
            return "GeneralAgent", False
        
        # SALES 에이전트는 RAG가 필요한 경우 플래그 설정
        return "SalesAgent", rag_needed
    
    async def handle_message(
        self, 
        message: str, 
        chat_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        적절한 에이전트를 결정하기 위해 메시지를 처리합니다.
        
        응답을 생성하는 대신, 이 에이전트는 어떤 에이전트가
        메시지를 처리해야 하는지 결정하고 그 정보를 반환합니다.
        또한 RAG 플래그를 포함합니다.
        
        인자:
            message: 사용자 메시지
            chat_history: 대화 기록
            
        반환값:
            라우팅 결정을 포함하는 딕셔너리
        """
        # 적절한 에이전트와 RAG 필요 여부 결정
        target_agent, use_rag = await self.determine_agent(message)
        
        # 라우팅 결정을 핸드오프로 반환
        return {
            "agent_name": self.name,
            "response": f"Message routed to {target_agent}",
            "handoff_to": target_agent,
            "use_rag": use_rag
        } 