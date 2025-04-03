"""
Sales Agent - Handles product recommendations and sales inquiries

This agent specializes in handling insurance product inquiries,
making recommendations, and generating relevant questions to gather
missing information from the user.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from openai import AsyncOpenAI
from dotenv import load_dotenv

from agents.core.agent_base import AgentBase
from agents.core.orchestrator import handoff_to
from agents.core.rag_agent import RAGEngine

# Load environment variables
load_dotenv()

class SalesAgent(AgentBase):
    """
    Agent responsible for handling insurance sales and product recommendations.
    
    This agent specializes in answering insurance-related questions,
    recommending appropriate products, and generating questions to
    gather missing information from the user.
    """
    
    def __init__(self, name: str = "SalesAgent"):
        """
        Initialize the sales agent.
        
        Args:
            name: Name of the agent
        """
        # Define the system message for the sales agent
        system_message = """당신은 한화손해보험의 운전자보험 전문 상담사입니다. 고객 응대 시 다음 지침을 따르세요:

1. 고객의 필요와 상황에 맞는 상품을 추천하세요.
2. 보험 상품의 주요 보장내용과 특징을 명확하게 설명하세요.
3. 고객의 질문에 정확하고 상세하게 답변하세요.
4. 필요한 정보가 부족할 경우, 추가 질문을 통해 정보를 수집하세요.

한화손해보험의 주요 운전자보험 상품은 다음과 같습니다:
- 차도리운전자보험: 기본적인 보장을 제공하는 표준 상품
- 차도리운전자보험Plus: 보장 범위가 확대된 프리미엄 상품
- 차도리ECO운전자보험: 친환경 차량 특화 상품
- 차도리운전자보험VIP: 최고 수준의 보장을 제공하는 프리미엄 상품

고객의 질문에 대해 자세하고 정확한 정보를 제공하기 위해 지식 검색 도구를 활용하세요.
일반적인 질문에 답변할 수 없는 경우 GeneralAgent로 대화를 전환하세요.
"""
        
        # Create handoff functions
        @handoff_to("GeneralAgent")
        def transfer_to_general():
            """보험 상품 외 일반적인 질문은 일반 상담 에이전트로 전환합니다."""
            pass
        
        # Initialize the base class with tools
        super().__init__(
            name=name,
            system_message=system_message,
            tools=[
                self.generate_next_questions,
                self.generate_recommendation,
                transfer_to_general
            ]
        )
        
        # Initialize the OpenAI client
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize RAG engine (but don't use it by default)
        self.rag_engine = RAGEngine(collection_name="insurance_products")
        self.use_rag = False
    
    async def generate_next_questions(self, profile_data: Optional[str] = None) -> str:
        """
        Generate questions to gather missing information from the user.
        
        Args:
            profile_data: JSON string of the current user profile data
            
        Returns:
            A string containing suggested questions
        """
        if not profile_data:
            return "프로필 정보가 없습니다. 질문을 생성할 수 없습니다."
        
        try:
            # Parse the profile data
            profile = json.loads(profile_data) if isinstance(profile_data, str) else profile_data
            
            # Use RAG if enabled
            rag_context = ""
            if self.use_rag:
                try:
                    # Convert profile information to a search query
                    profile_summary = ", ".join([f"{k}:{v}" for k, v in profile.items() if k in ["age", "driving_experience", "vehicle_type"]])
                    rag_prompt = f"운전자보험을 위해 필요한 정보 {profile_summary}"
                    
                    # Get context from the RAG engine
                    rag_context = await self.rag_engine.generate_context(rag_prompt)
                except Exception as e:
                    print(f"[SalesAgent] RAG context generation error (ignored): {str(e)}")
            
            # Create the prompt
            prompt = f"""
{rag_context if rag_context else ""}

현재 고객 프로필 정보를 기반으로, 운전자보험 상담/추천을 위해 필요한 추가 질문을 생성해주세요.
질문은 자연스러운 대화 형식으로 생성하고, 고객이 아직 제공하지 않은 정보를 수집하는 데 중점을 두어야 합니다.

현재 프로필 정보:
{json.dumps(profile, ensure_ascii=False, indent=2)}

다음 정보가 누락된 경우 관련 질문을 생성하세요:
- 연령
- 운전 경력 (년수)
- 차량 종류 (일반 자동차, 친환경 차량 등)
- 주행 환경 (도심, 고속도로, 장거리 등)
- 보험 예산
- 특별히 중요하게 생각하는 보장 사항

3-5개의 간결하고 구체적인 질문을 생성해주세요.
"""
            
            # Call the OpenAI API
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[SalesAgent] Error generating questions: {str(e)}")
            return "질문 생성 중 오류가 발생했습니다."
    
    async def generate_recommendation(self, profile_data: Optional[str] = None) -> str:
        """
        Generate insurance product recommendations based on the user profile.
        
        Args:
            profile_data: JSON string of the current user profile data
            
        Returns:
            A string containing product recommendations
        """
        if not profile_data:
            return "프로필 정보가 없습니다. 추천을 생성할 수 없습니다."
        
        try:
            # Parse the profile data
            profile = json.loads(profile_data) if isinstance(profile_data, str) else profile_data
            
            # Use RAG if enabled
            rag_context = ""
            if self.use_rag:
                try:
                    # Create query for product information retrieval
                    recommendation_query = "운전자보험 추천 차도리운전자보험 차도리운전자보험Plus 차도리ECO운전자보험 차도리운전자보험VIP"
                    
                    # Get product information from the RAG engine
                    rag_context = await self.rag_engine.generate_context(recommendation_query)
                except Exception as e:
                    print(f"[SalesAgent] RAG context generation error (ignored): {str(e)}")
            
            # Create the prompt
            prompt = f"""
{rag_context if rag_context else ""}

현재 고객 프로필 정보를 기반으로, 가장 적합한 운전자보험 상품을 추천해주세요.
추천은 고객의 운전 습관, 보험 요구사항, 예산 등을 고려해야 합니다.

현재 프로필 정보:
{json.dumps(profile, ensure_ascii=False, indent=2)}

추천 상품의 주요 특징과 해당 고객에게 적합한 이유를 간결하게 설명해주세요.
"""
            
            # Call the OpenAI API
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[SalesAgent] Error generating recommendations: {str(e)}")
            return "추천 생성 중 오류가 발생했습니다."
    
    async def handle_message(
        self, 
        message: str, 
        chat_history: List[Dict[str, Any]],
        use_rag: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Process a message and generate a response.
        
        This override includes profile information from the chat history 
        to help the agent make better responses.
        
        Args:
            message: The user message
            chat_history: The conversation history
            use_rag: Whether to use RAG for this message
            
        Returns:
            A dictionary containing the agent's response
        """
        # Set RAG flag if specified
        if use_rag is not None:
            self.use_rag = use_rag
        
        # Check if there's any profile information in the chat history
        profile_info = None
        for msg in reversed(chat_history):
            if msg.get("role") == "system" and "profile_info" in msg.get("content", ""):
                try:
                    profile_info = msg.get("content").split("profile_info: ")[1]
                except:
                    pass
                break
        
        # Handle general inquiries
        if self._is_general_inquiry(message):
            return {
                "agent_name": self.name,
                "response": "일반 상담 에이전트로 연결해 드리겠습니다.",
                "handoff_to": "GeneralAgent"
            }
        
        # Enhanced message with profile and RAG context if enabled
        enhanced_message = message
        
        # If there's profile information, include it in the message to the agent
        if profile_info:
            enhanced_message = f"{message}\n\n[System: 고객 프로필 정보: {profile_info}]"
        
        # If RAG is enabled, add relevant context
        if self.use_rag:
            try:
                rag_context = await self.rag_engine.generate_context(message)
                if rag_context:
                    enhanced_message = f"{enhanced_message}\n\n[System: 관련 정보:\n{rag_context}]"
            except Exception as e:
                print(f"[SalesAgent] RAG context generation error (ignored): {str(e)}")
        
        # Process the message with the enhanced information
        return await super().handle_message(enhanced_message, chat_history)
    
    def _is_general_inquiry(self, message: str) -> bool:
        """
        Determine if a message is a general conversation.
        
        Args:
            message: The user message
            
        Returns:
            Whether the message is a general inquiry
        """
        # General conversation keywords
        general_keywords = [
            "안녕", "반가워", "고마워", "감사", "날씨", "기분", "오늘", 
            "어때", "잘 지내", "방가", "ㅎㅎ", "ㅋㅋ"
        ]
        
        return any(keyword in message for keyword in general_keywords) 