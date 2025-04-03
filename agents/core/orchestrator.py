"""
오케스트레이터 - 에이전트 전환 및 대화 흐름 관리

이 모듈은 여러 전문 에이전트 간의 대화를 관리하고
에이전트 간 전환(핸드오프)을 처리하는 핵심 오케스트레이션 로직을 제공합니다.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from datetime import datetime

from autogen import ConversableAgent
from agents.core.agent_registry import AgentRegistry
from agents.core.agent_base import AgentBase

class Orchestrator:
    """
    에이전트와 사용자 간의 대화 흐름을 관리합니다.
    
    오케스트레이터는 다음을 담당합니다:
    1. 적절한 에이전트로 대화 시작
    2. 에이전트가 제어권을 넘길 때 에이전트 전환 처리
    3. 에이전트 전환 과정에서 대화 기록 유지
    4. 에이전트 전환 시 컨텍스트 제공
    """
    
    def __init__(self):
        """오케스트레이터를 초기화합니다."""
        self.conversation_history = []
        self.current_agent_name = None
        self.agents = AgentRegistry()  # 등록된 모든 에이전트에 접근
        self.use_rag = False  # RAG 사용 여부 플래그
        
    async def process_message(
        self, 
        message: str, 
        agent_name: Optional[str] = None,
        use_rag: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        사용자 메시지를 처리하고 적절한 에이전트로부터 응답을 받습니다.
        
        인자:
            message: 처리할 사용자 메시지
            agent_name: 사용할 특정 에이전트 (None이면 자동 라우팅)
            use_rag: RAG 기능 사용 여부
            
        반환값:
            응답과 메타데이터를 포함하는 딕셔너리
        """
        # 사용자 메시지를 대화 기록에 추가
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 특정 에이전트가 요청되지 않은 경우, 현재 에이전트를 사용하거나 새로 결정
        if not agent_name:
            agent_name, determined_rag = await self._determine_agent(message)
            # 상위 레벨에서 RAG 플래그가 명시적으로 설정되지 않은 경우 결정된 값 사용
            if use_rag is None:
                use_rag = determined_rag
        
        # 에이전트 인스턴스 가져오기
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"에이전트 '{agent_name}'가 레지스트리에 없습니다")
        
        # 현재 RAG 상태 저장
        self.use_rag = use_rag if use_rag is not None else self.use_rag
        
        # 선택된 에이전트로 메시지 처리 (RAG 플래그 전달)
        self.current_agent_name = agent_name
        
        # RAG 사용 여부를 handle_message에 전달 (SalesAgent만 RAG를 사용)
        if agent_name == "SalesAgent" and hasattr(agent, "handle_message") and "use_rag" in agent.handle_message.__code__.co_varnames:
            response_data = await agent.handle_message(message, self.conversation_history, use_rag=self.use_rag)
        else:
            response_data = await agent.handle_message(message, self.conversation_history)
        
        # 다른 에이전트로의 전환이 요청되었는지 확인
        handoff_to = response_data.get("handoff_to")
        if handoff_to and handoff_to != agent_name:
            # 전환 정보를 대화 기록에 추가
            self.conversation_history.append({
                "role": "system",
                "content": f"대화가 {agent_name}에서 {handoff_to}로 전환되었습니다",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"handoff": True, "from": agent_name, "to": handoff_to}
            })
            
            # 동일한 메시지로 새 에이전트를 호출하되 전환 컨텍스트 포함
            handoff_message = f"{message}\n\n[시스템: 대화가 {agent_name}에서 전환되었습니다. 이전 응답: {response_data['response']}]"
            self.current_agent_name = handoff_to
            
            # 새 에이전트로 처리
            new_agent = self.agents.get(handoff_to)
            if not new_agent:
                raise ValueError(f"전환 대상 에이전트 '{handoff_to}'가 레지스트리에 없습니다")
            
            # RAG 플래그 전달 (SalesAgent만 해당)
            if handoff_to == "SalesAgent" and hasattr(new_agent, "handle_message") and "use_rag" in new_agent.handle_message.__code__.co_varnames:
                response_data = await new_agent.handle_message(handoff_message, self.conversation_history, use_rag=self.use_rag)
            else:
                response_data = await new_agent.handle_message(handoff_message, self.conversation_history)
        
        # 에이전트의 응답을 대화 기록에 추가
        self.conversation_history.append({
            "role": "assistant",
            "agent": response_data["agent_name"],
            "content": response_data["response"],
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": response_data["response"],
            "agent": response_data["agent_name"],
            "handoff_occurred": handoff_to is not None,
            "previous_agent": agent_name if handoff_to else None,
            "current_agent": response_data["agent_name"],
            "use_rag": self.use_rag
        }
    
    async def _determine_agent(self, message: str) -> Tuple[str, bool]:
        """
        주어진 메시지를 처리할 에이전트를 결정합니다.
        
        인자:
            message: 사용자 메시지
            
        반환값:
            메시지를 처리할 에이전트의 이름과 RAG 사용 여부를 포함하는 튜플
        """
        # 현재 에이전트가 있으면 그것을 사용
        if self.current_agent_name:
            return self.current_agent_name, self.use_rag
        
        # 라우터 에이전트가 사용 가능한지 확인
        router = self.agents.get("RouterAgent")
        if router:
            # 라우터 에이전트로 메시지 분류
            result = await router.handle_message(message, self.conversation_history)
            # 라우터가 결정한 에이전트와 RAG 사용 여부 반환
            return result.get("handoff_to", "GeneralAgent"), result.get("use_rag", False)
            
        # 라우터가 없으면 기본 에이전트 중 하나 반환
        available_agents = self.agents.list_agents()
        if len(available_agents) > 0:
            return available_agents[0], False
            
        raise ValueError("레지스트리에 사용 가능한 에이전트가 없습니다")
    
    def reset_conversation(self) -> None:
        """대화 기록과 현재 에이전트를 초기화합니다."""
        self.conversation_history = []
        self.current_agent_name = None
        self.use_rag = False
    
    def get_conversation_summary(self) -> str:
        """
        대화 요약을 가져옵니다.
        
        반환값:
            대화를 요약한 문자열
        """
        # TODO: 더 정교한 요약 기능 구현
        # 지금은 마지막 몇 턴만 컴파일
        summary = "대화 요약:\n"
        
        for msg in self.conversation_history[-10:]:  # 마지막 10개 메시지
            role = msg["role"]
            if role == "user":
                summary += f"사용자: {msg['content']}\n"
            elif role == "assistant":
                agent = msg.get("agent", "에이전트")
                summary += f"{agent}: {msg['content']}\n"
            elif role == "system":
                summary += f"시스템: {msg['content']}\n"
                
        return summary

# 핸드오프 도구 생성을 위한 데코레이터
def handoff_to(target_agent_name: str) -> Callable:
    """
    핸드오프 도구 함수를 생성하는 데코레이터.
    
    인자:
        target_agent_name: 전환할 에이전트의 이름
        
    반환값:
        핸드오프를 트리거하는 데코레이트된 함수
    """
    def decorator(func: Callable) -> Callable:
        func._is_handoff = True
        
        # 원래 docstring을 유지하거나 기본값 생성
        if not func.__doc__:
            func.__doc__ = f"대화를 {target_agent_name} 에이전트로 전환합니다."
            
        def wrapper(*args, **kwargs) -> Dict:
            # 핸드오프에 대한 정보 반환
            return {"handoff_to": target_agent_name}
            
        # 원래 함수에서 메타데이터 복사
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper._is_handoff = True
        wrapper._target_agent = target_agent_name
        
        return wrapper
        
    return decorator 