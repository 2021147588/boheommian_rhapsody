import os
import json
import inspect
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def function_to_schema(func):
    """함수를 OpenAI 함수 스키마로 변환합니다."""
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    signature = inspect.signature(func)
    parameters = {}
    
    for param in signature.parameters.values():
        param_type = type_map.get(param.annotation, "string")
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }

class AgentResponse(BaseModel):
    agent: Any
    messages: List[Dict[str, Any]]

class AdvancedBaseAgent:
    def __init__(self, name: str, system_message: str, model: str = "gpt-3.5-turbo", tools: List[Callable] = None):
        self.name = name
        self.system_message = system_message
        self.model = model
        self.tools = tools or []
    
    def run_interaction(self, messages: List[Dict[str, Any]]) -> AgentResponse:
        """
        에이전트와 상호작용하고 응답을 반환합니다.
        핸드오프가 발생하면 새 에이전트를 반환합니다.
        """
        current_agent = self
        num_init_messages = len(messages)
        messages = messages.copy()
        # breakpoint()
        while True:
            # 도구 스키마와 도구 맵 준비
            tool_schemas = [function_to_schema(tool) for tool in current_agent.tools]
            tools_map = {tool.__name__: tool for tool in current_agent.tools}
            
            # OpenAI 완성 가져오기
            response = client.chat.completions.create(
                model=current_agent.model,
                messages=[{"role": "system", "content": current_agent.system_message}] + messages,
                tools=tool_schemas if tool_schemas else None,
            )
            message = response.choices[0].message
            messages.append({"role": "assistant", "content": message.content, "tool_calls": message.tool_calls})
            
            if message.content:
                print(f"{current_agent.name}: {message.content}")
            
            if not message.tool_calls:
                break
            
            # 도구 호출 처리
            for tool_call in message.tool_calls:
                result = self._execute_tool_call(tool_call, tools_map, current_agent.name)
                
                # 에이전트 핸드오프 처리
                if isinstance(result, AdvancedBaseAgent):
                    current_agent = result
                    result = f"핸드오프: {current_agent.name}로 전환되었습니다."
                
                result_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
                messages.append(result_message)
        
        # 사용된 마지막 에이전트와 새 메시지 반환
        return AgentResponse(agent=current_agent, messages=messages[num_init_messages:])
    
    def _execute_tool_call(self, tool_call, tools_map, agent_name):
        """
        도구 호출을 실행하고 결과를 반환합니다.
        """
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        print(f"{agent_name}: {name}({args})")
        
        # 해당 함수를 인수와 함께 호출
        return tools_map[name](**args)
    
    def get_agent(self):
        """현재 에이전트를 반환합니다."""
        return self 