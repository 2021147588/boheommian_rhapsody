"""
에이전트 기본 클래스 - 핸드오프 기능이 있는 전문 에이전트 생성을 위한 핵심 프레임워크

이 모듈은 AutoGen의 AssistantAgent를 확장하여 에이전트 루틴 및 
전문 에이전트 간 핸드오프를 위한 추가 기능을 제공합니다.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from autogen import AssistantAgent, ConversableAgent
from dotenv import load_dotenv

from agents.core.agent_registry import AgentRegistry

# 환경 변수 로드
load_dotenv()

class AgentBase:
    """
    시스템 내 모든 전문 에이전트를 위한 기본 클래스.
    
    이 클래스는 AutoGen AssistantAgent를 래핑하고 루틴을 따르고
    전문 에이전트 간의 핸드오프에 참여하는 기능을 확장합니다.
    """
    
    def __init__(
        self,
        name: str,
        system_message: str,
        tools: List[Callable] = None,
        model: str = "gpt-4o-mini",
        api_key: str = None,
        register: bool = True
    ):
        """
        새 에이전트를 초기화합니다.
        
        인자:
            name: 에이전트 이름
            system_message: 에이전트의 행동/루틴을 정의하는 시스템 메시지
            tools: 에이전트가 사용할 수 있는 도구 함수 목록
            model: 사용할 LLM 모델
            api_key: OpenAI API 키 (기본값은 환경 변수)
            register: 이 에이전트를 글로벌 레지스트리에 등록할지 여부
        """
        self.name = name
        self.system_message = system_message
        self.tools = tools or []
        
        # AutoGen 에이전트 구성
        self.agent = AssistantAgent(
            name=name,
            system_message=system_message,
            llm_config={
                "config_list": [
                    {
                        "model": model,
                        "api_key": api_key or os.getenv("OPENAI_API_KEY")
                    }
                ],
                "tools": self._prepare_tools()
            }
        )
        
        # 요청 시 글로벌 레지스트리에 등록
        if register:
            AgentRegistry.register(name, self)
    
    def _prepare_tools(self) -> List[Dict]:
        """
        AutoGen 에이전트용 도구를 준비합니다.
        
        이 메서드는 Python 함수 도구를 AutoGen에서 예상하는 형식으로 변환합니다.
        
        반환값:
            AutoGen용 도구 명세 목록
        """
        prepared_tools = []
        
        # 에이전트의 모든 도구 포함
        if self.tools:
            for tool in self.tools:
                # 다른 에이전트로의 핸드오프를 위한 도구인 경우
                if hasattr(tool, '_is_handoff') and tool._is_handoff:
                    prepared_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.__name__,
                            "description": tool.__doc__ or f"{tool.__name__.replace('transfer_to_', '')}로 전환",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    })
                # 일반 도구 함수인 경우
                else:
                    # 함수 시그니처와 문서 문자열 추출
                    import inspect
                    signature = inspect.signature(tool)
                    docstring = tool.__doc__ or ""
                    
                    # 매개변수 정보 구성
                    properties = {}
                    required = []
                    
                    for param_name, param in signature.parameters.items():
                        param_type = "string"  # 기본 타입
                        if param.annotation != inspect.Parameter.empty:
                            if param.annotation == int:
                                param_type = "integer"
                            elif param.annotation == float:
                                param_type = "number"
                            elif param.annotation == bool:
                                param_type = "boolean"
                        
                        properties[param_name] = {"type": param_type}
                        
                        # 매개변수에 기본값이 없으면 필수
                        if param.default == inspect.Parameter.empty:
                            required.append(param_name)
                    
                    prepared_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.__name__,
                            "description": docstring,
                            "parameters": {
                                "type": "object",
                                "properties": properties,
                                "required": required
                            }
                        }
                    })
        
        # 특별 케이스: 이미 핸드오프 도구가 아닌 경우, 핸드오프 기능 항상 추가
        self._add_handoff_tools(prepared_tools)
        
        return prepared_tools
    
    def _add_handoff_tools(self, tools_list: List[Dict]) -> None:
        """에이전트의 도구에 핸드오프 기능을 추가합니다"""
        # 추가 확장 가능
        pass
    
    def register_tools(self, tools: List[Callable]) -> None:
        """
        에이전트에 추가 도구를 등록합니다.
        
        인자:
            tools: 등록할 도구 함수 목록
        """
        self.tools.extend(tools)
        # 에이전트의 도구 업데이트
        self.agent.llm_config["tools"] = self._prepare_tools()
    
    async def handle_message(
        self, 
        message: str, 
        chat_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        메시지를 처리하고 응답을 생성합니다.
        
        인자:
            message: 처리할 사용자 메시지
            chat_history: 이전 대화 기록
            
        반환값:
            에이전트 응답과 핸드오프 표시를 포함하는 딕셔너리
        """
        # 상호작용을 위한 임시 사용자 에이전트 생성
        temp_user = ConversableAgent(name="User", llm_config=None)
        
        # 에이전트용 메시지 준비
        input_message = {"role": "user", "content": message}
        
        if not chat_history:
            chat_history = []
        
        # 기록과 새 메시지 결합
        messages = chat_history + [input_message]
        
        # 에이전트의 응답 가져오기
        response = await self._get_agent_response(temp_user, messages)
        
        # 응답에서 핸드오프 요청 확인
        handoff_to = None
        if isinstance(response, dict) and response.get("handoff_to"):
            handoff_to = response["handoff_to"]
            
        return {
            "agent_name": self.name,
            "response": response if isinstance(response, str) else response.get("content", ""),
            "handoff_to": handoff_to
        }
    
    async def _get_agent_response(
        self, 
        user_agent: ConversableAgent, 
        messages: List[Dict[str, Any]]
    ) -> Union[str, Dict[str, Any]]:
        """
        에이전트로부터 비동기적으로 응답을 가져옵니다.
        
        인자:
            user_agent: 상호작용을 위한 임시 사용자 에이전트
            messages: 대화 기록
            
        반환값:
            에이전트의 응답
        """
        # AutoGen의 generate_reply는 비동기가 아니므로 별도 스레드에서 실행해야 함
        loop = asyncio.get_event_loop()
        
        def _generate_reply():
            return self.agent.generate_reply(sender=user_agent, messages=messages)
        
        # 동기 메서드를 스레드 풀에서 실행
        response = await loop.run_in_executor(None, _generate_reply)
        
        # 핸드오프를 나타낼 수 있는 도구 호출 파싱 및 확인
        # 응답에 함수 호출이 포함되어 있는지 확인
        if hasattr(self.agent, 'last_tool_call') and self.agent.last_tool_call:
            tool_call = self.agent.last_tool_call
            
            # 도구 호출이 핸드오프인지 확인
            for tool in self.tools:
                if (hasattr(tool, '_is_handoff') and tool._is_handoff and 
                    hasattr(tool, '_target_agent') and 
                    tool.__name__ == tool_call.get('name')):
                    
                    # 핸드오프 표시 반환
                    return {"content": response, "handoff_to": tool._target_agent}
        
        return response 