from .base import Agent
from typing import List, Dict

class GeneralAgent(Agent):
    def __init__(self, **data):
        super().__init__(**data)
        self.instructions = """You are a general purpose insurance consultation bot.
        
        Your responsibilities:
        1. Handle general insurance inquiries
        2. Route complex queries to specialized agents
        3. Maintain conversation context
        4. Provide basic insurance information
        5. Ensure smooth handoffs between different agents
        
        Always maintain a helpful and professional demeanor."""
        
        self.tools = [
            self.route_to_specialist,
            self.get_basic_info,
            self.log_conversation
        ]
    
    def route_to_specialist(self, query_type: str) -> str:
        """Determine which specialist agent should handle the query"""
        # Implementation will be added
        pass
    
    def get_basic_info(self, topic: str) -> Dict:
        """Retrieve basic insurance information"""
        # Implementation will be added
        pass
    
    def log_conversation(self, interaction: Dict) -> bool:
        """Log the conversation flow and routing decisions"""
        # Implementation will be added
        pass 