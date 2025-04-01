from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from openai import OpenAI
import inspect
import json

class Agent(BaseModel):
    name: str
    instructions: str
    model: str = "gpt-4"
    tools: List[Any] = []
    conversation_history: List[Dict] = []
    
    def __init__(self, **data):
        super().__init__(**data)
        self.client = OpenAI()
        
    def function_to_schema(self, func) -> dict:
        """Convert Python function to OpenAI function schema"""
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
    
    def execute_tool_call(self, tool_call, tools_map):
        """Execute a tool call and return the result"""
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        print(f"{self.name}: {name}({args})")
        return tools_map[name](**args)
    
    def run_conversation(self, user_input: str) -> str:
        """Run a single turn of conversation"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Prepare tools
        tool_schemas = [self.function_to_schema(tool) for tool in self.tools]
        tools_map = {tool.__name__: tool for tool in self.tools}
        
        while True:
            # Get completion from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": self.instructions}] + self.conversation_history,
                tools=tool_schemas if tool_schemas else None
            )
            
            assistant_message = response.choices[0].message
            self.conversation_history.append(assistant_message)
            
            if assistant_message.content:
                print(f"{self.name}:", assistant_message.content)
            
            # Handle any tool calls
            if not assistant_message.tool_calls:
                break
                
            for tool_call in assistant_message.tool_calls:
                result = self.execute_tool_call(tool_call, tools_map)
                
                result_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                }
                self.conversation_history.append(result_message)
        
        return assistant_message.content 