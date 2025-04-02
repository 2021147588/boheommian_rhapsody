from typing import List, Dict, Any, Optional
from autogen import Agent, AssistantAgent, UserProxyAgent
import os

class InsuranceAgent(Agent):
    def __init__(self, name: str, role: str, **kwargs):
        super().__init__(
            name=name,
            system_message=f"""You are an insurance {role} agent. Your role is to:
            1. Understand customer needs and concerns
            2. Provide relevant insurance information
            3. Help customers make informed decisions
            4. Maintain professional and empathetic communication
            5. Follow up on customer inquiries
            
            Always be helpful, clear, and focused on finding the best insurance solution for the customer.""",
            llm_config={
                "config_list": [{
                    "model": "gpt-4",
                    "api_key": os.environ.get("OPENAI_API_KEY")
                }],
                "temperature": 0.7
            },
            **kwargs
        )

class SalesAgent(InsuranceAgent):
    def __init__(self, **kwargs):
        super().__init__(
            name="Sales Agent",
            role="sales",
            system_message="""You are an insurance sales specialist. Your focus is on:
            1. Identifying customer needs and pain points
            2. Presenting relevant insurance solutions
            3. Overcoming objections professionally
            4. Closing sales effectively
            5. Building long-term customer relationships
            
            Use a consultative approach and focus on value proposition.""",
            **kwargs
        )

class TechnicalAgent(InsuranceAgent):
    def __init__(self, **kwargs):
        super().__init__(
            name="Technical Agent",
            role="technical",
            system_message="""You are an insurance technical specialist. Your expertise includes:
            1. Detailed policy explanations
            2. Coverage analysis
            3. Risk assessment
            4. Technical documentation
            5. Compliance information
            
            Provide accurate and detailed technical information while maintaining clarity.""",
            **kwargs
        )

class CustomerServiceAgent(InsuranceAgent):
    def __init__(self, **kwargs):
        super().__init__(
            name="Customer Service Agent",
            role="customer service",
            system_message="""You are an insurance customer service representative. Your responsibilities:
            1. Handling customer inquiries
            2. Resolving issues
            3. Processing requests
            4. Providing policy information
            5. Ensuring customer satisfaction
            
            Focus on excellent service and quick resolution.""",
            **kwargs
        )

class HumanProxy(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            name="Human",
            system_message="You are a human customer interacting with insurance agents.",
            human_input_mode="ALWAYS",
            llm_config=False,
            **kwargs
        ) 