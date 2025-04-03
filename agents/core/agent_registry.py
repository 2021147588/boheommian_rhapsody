"""
에이전트 레지스트리 - 시스템의 모든 에이전트 등록 및 접근 관리

이 모듈은 모든 에이전트를 위한 중앙 레지스트리를 제공하여 이름으로 접근할 수 있게 하고
다양한 전문 에이전트 간의 핸드오프를 가능하게 합니다.
"""

from typing import Dict, Type, Optional, Any
from autogen import Agent

class AgentRegistry:
    """
    시스템 내 에이전트를 관리하고 접근하기 위한 레지스트리.
    
    이 클래스는 오케스트레이션 시스템에서 사용 가능한 모든 에이전트의
    단일 글로벌 레지스트리를 유지하여 이름으로 접근할 수 있게 하고
    다양한 전문 에이전트 간의 핸드오프를 용이하게 합니다.
    """
    
    _instance = None
    _agents: Dict[str, Agent] = {}
    
    def __new__(cls):
        """레지스트리가 하나만 존재하도록 하는 싱글톤 패턴"""
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, name: str, agent: Agent) -> None:
        """
        레지스트리에 에이전트를 등록합니다.
        
        인자:
            name: 에이전트의 고유 식별자
            agent: 등록할 에이전트 인스턴스
        """
        cls._agents[name] = agent
        
    @classmethod
    def get(cls, name: str) -> Optional[Agent]:
        """
        이름으로 에이전트를 검색합니다.
        
        인자:
            name: 검색할 에이전트의 이름
            
        반환값:
            에이전트 인스턴스 또는 찾을 수 없는 경우 None
        """
        return cls._agents.get(name)
    
    @classmethod
    def list_agents(cls) -> list:
        """등록된 모든 에이전트 이름의 목록을 반환합니다"""
        return list(cls._agents.keys())
    
    @classmethod
    def reset(cls) -> None:
        """등록된 모든 에이전트를 지웁니다"""
        cls._agents.clear() 