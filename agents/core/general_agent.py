"""
일반 에이전트 - 일반적인 문의와 대화 처리

이 에이전트는 일반적인 대화, 일상 대화 및
사용자의 보험과 관련되지 않은 문의를 처리하는 데 특화되어 있습니다.
"""

import os
from typing import Dict, List, Any

from agents.core.agent_base import AgentBase
from agents.core.orchestrator import handoff_to

class GeneralAgent(AgentBase):
    """
    일반적인 대화와 문의를 처리하는 에이전트.
    
    이 에이전트는 일상 대화와 보험 상품이나 서비스와
    특별히 관련되지 않은 일반적인 질문을 처리하도록 설계되었습니다.
    """
    
    def __init__(self, name: str = "GeneralAgent"):
        """
        일반 에이전트를 초기화합니다.
        
        인자:
            name: 에이전트 이름
        """
        # 일반 에이전트의 시스템 메시지 정의
        system_message = """당신은 금융 회사의 고객 서비스 에이전트입니다. 고객과의 일반적인
대화와 보험/금융 외 질문을 처리하는 역할을 합니다.
 
다음 지침을 따르세요:
1. 친절하고 도움이 되는 방식으로 응대하세요.
2. 고객의 이름이 있다면 이를 사용하여 개인화된 응대를 하세요.
3. 간결하고 명확한 응답을 제공하세요.
4. 보험이나 금융 상품에 관한 전문적인 질문이 들어오면 SalesAgent로 전환하세요.
5. 보험 상품 추천 요청이 들어오면 SalesAgent로 전환하세요.
6. 운전자보험에 대한 구체적인 질문이 들어오면 SalesAgent로 전환하세요.
7. 짧고 간결한 응답을 제공하세요.
"""
        
        # 핸드오프 함수 생성
        @handoff_to("SalesAgent")
        def transfer_to_sales():
            """보험 상품 관련 질문은 상품 전문 에이전트로 전환합니다."""
            pass
        
        # 도구와 함께 기본 클래스 초기화
        super().__init__(
            name=name,
            system_message=system_message,
            tools=[transfer_to_sales]
        )
    
    async def handle_message(
        self, 
        message: str, 
        chat_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        사용자 메시지를 처리하고 응답을 생성합니다.
        
        이 구현은 메시지에 보험 관련 질문이 포함되어 있는지 확인하고
        필요할 때 적절한 전문 에이전트로 전환하는 데 중점을 둡니다.
        
        인자:
            message: 사용자 메시지
            chat_history: 대화 기록
            
        반환값:
            에이전트의 응답
        """
        # 응답을 개인화하기 위해 대화 기록에서 사용자 이름 찾기
        user_name = None
        for msg in chat_history:
            if msg.get("role") == "system" and "profile" in msg.get("content", "").lower():
                content = msg.get("content", "")
                if "name" in content.lower():
                    # 이름 언급 추출 (간단한 접근법)
                    parts = content.split("name:")
                    if len(parts) > 1:
                        user_name = parts[1].split(",")[0].strip()
                        break
        
        # 사용자 이름이 있으면 메시지 개인화
        if user_name:
            enhanced_message = f"{message}\n\n[System: 고객 이름은 {user_name}입니다.]"
        else:
            enhanced_message = message
            
        # 메시지 처리
        return await super().handle_message(enhanced_message, chat_history) 