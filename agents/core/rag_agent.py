"""
RAG Agent - Provides knowledge retrieval for other agents

This agent implements a retrieval-augmented generation system that can be used
to enhance responses with relevant knowledge from a document database.
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from openai import AsyncOpenAI
from dotenv import load_dotenv

from agents.core.agent_base import AgentBase

# Load environment variables
load_dotenv()

class RAGEngine:
    """
    Retrieval-Augmented Generation Engine.
    
    This engine retrieves relevant information from a knowledge base
    to enhance agent responses with factual context.
    """
    
    def __init__(self, collection_name: str = "default"):
        """
        Initialize the RAG engine.
        
        Args:
            collection_name: Name of the document collection to query
        """
        self.collection_name = collection_name
        
        # Temporary knowledge base for demonstration (will be replaced by actual DB)
        self.temp_knowledge_base = {
            "insurance_products": {
                "차도리운전자보험": """
                차도리운전자보험은 교통사고와 일상생활 중 발생할 수 있는 각종 위험을 보장하는 상품입니다.
                주요 보장 내용:
                - 자동차사고 벌금 보장 (최대 2,000만원)
                - 교통사고 처리지원금 (최대 1억원)
                - 자동차사고 변호사선임비용 (500만원)
                - 골절진단비, 화상진단비 (20만원)
                - 일반상해 입원일당 (1일당 1만원)
                """,
                
                "차도리운전자보험Plus": """
                차도리운전자보험Plus는 기본형에 추가 보장을 제공하는 확장 상품입니다.
                주요 보장 내용:
                - 자동차사고 벌금 보장 (최대 4,000만원)
                - 교통사고 처리지원금 (최대 2억원)
                - 자동차사고 변호사선임비용 (1,000만원)
                - 골절진단비, 화상진단비 (50만원)
                - 일반상해 입원일당 (1일당 2만원)
                - 운전중 교통사고 처리지원금 (3,000만원)
                - 보이스피싱 손해 (100만원)
                """,
                
                "차도리ECO운전자보험": """
                차도리ECO운전자보험은 친환경 운전을 장려하는 특약이 포함된 상품입니다.
                주요 보장 내용:
                - 친환경차 충전 중 상해 (3,000만원)
                - 자동차사고 벌금 보장 (최대 3,000만원)
                - 교통사고 처리지원금 (최대 1억5천만원)
                - 자동차사고 변호사선임비용 (700만원)
                - 친환경차 할인 특약 (전기차, 하이브리드차)
                """,
                
                "차도리운전자보험VIP": """
                차도리운전자보험VIP는 최고 수준의 보장을 제공하는 프리미엄 상품입니다.
                주요 보장 내용:
                - 자동차사고 벌금 보장 (최대 6,000만원)
                - 교통사고 처리지원금 (최대 3억원)
                - 자동차사고 변호사선임비용 (1,500만원)
                - 골절진단비, 화상진단비 (100만원)
                - 일반상해 입원일당 (1일당 5만원)
                - 운전중 교통사고 처리지원금 (5,000만원)
                - 보이스피싱 손해 (500만원)
                - VIP 전담 보상 서비스
                """
            },
            "insurance_terms": {
                "교통사고 처리지원금": """
                교통사고 처리지원금이란 피보험자가 운전 중 자동차사고로 타인을
                사망하게 하거나 중대법규위반 교통사고로 피해자가 42일 이상 치료를
                요한다는 진단을 받은 경우, 검찰에 의해 공소제기되거나 자동차손해배상보장법에
                따라 경찰에 의해 송치되고 피보험자가 합의금을 지급한 경우 보험회사가
                피보험자에게 지급하는 금액입니다.
                """,
                
                "자동차사고 벌금": """
                자동차사고 벌금 특약은 피보험자가 운전 중 자동차사고로 타인의 신체에
                상해를 입혀 신체상해와 관련하여 벌금형을 받은 경우 보험회사가 벌금액을
                지급하는 특약입니다. 단, 특정범죄 가중처벌 등에 관한 법률 제5조의13에
                따른 어린이 보호구역에서 발생한 사고에 대해서는 별도의 보장한도가
                적용될 수 있습니다.
                """,
                
                "자동차사고 변호사선임비용": """
                자동차사고 변호사선임비용 특약은 피보험자가 운전 중 자동차사고로
                타인의 신체에 상해를 입혀 구속되거나 공소제기된 경우 또는 검사에
                의해 약식기소된 경우, 변호사선임비용을 지급하는 특약입니다.
                보험사는 실제로 발생한 변호사선임비용을 특약에서 정한 한도 내에서
                지급합니다.
                """
            },
            "faq": {
                "보험료 납입 방법": """
                보험료 납입 방법은 다음과 같습니다:
                1. 자동이체: 계좌에서 매월 자동으로 납부
                2. 신용카드: 등록된 카드로 자동 납부
                3. 모바일 앱: 한화손해보험 앱에서 간편 납부
                4. 인터넷 뱅킹: 계좌이체를 통한 납부
                5. 가상계좌: 전용 가상계좌 발급 후 납부
                """,
                
                "보험금 청구 방법": """
                보험금 청구 방법은 다음과 같습니다:
                1. 모바일 앱: 한화손해보험 앱에서 간편 청구
                2. 웹사이트: 한화손해보험 홈페이지에서 청구
                3. 고객센터: 1566-8000으로 전화하여 청구
                4. 지점 방문: 가까운 한화손해보험 지점 방문
                
                필요 서류:
                - 보험금 청구서
                - 신분증 사본
                - 사고 증명서류 (진단서, 치료비 영수증 등)
                - 통장 사본
                """,
                
                "계약 변경 방법": """
                계약 변경 방법은 다음과 같습니다:
                1. 고객센터: 1566-8000으로 전화하여 변경 요청
                2. 모바일 앱: 한화손해보험 앱에서 변경 신청
                3. 웹사이트: 한화손해보험 홈페이지에서 변경 신청
                4. 지점 방문: 가까운 한화손해보험 지점 방문
                
                변경 가능 항목:
                - 납입 방법/주기
                - 보험 가입금액
                - 특약 추가/삭제
                - 계약자/피보험자 정보 변경
                """
            }
        }
        
        # Initialize OpenAI client
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_context(self, query: str, max_documents: int = 3) -> str:
        """
        Generate context by retrieving relevant documents for a query.
        
        Args:
            query: The search query
            max_documents: Maximum number of documents to retrieve
            
        Returns:
            Context information as a string
        """
        # In production, this would use vector similarity search in a database
        # For now, use a simple keyword-based search
        
        results = []
        query_lower = query.lower()
        
        # Search through all collections in the knowledge base
        for collection_name, documents in self.temp_knowledge_base.items():
            for doc_title, doc_content in documents.items():
                # Simple keyword matching (would be replaced by proper vector search)
                if any(keyword.lower() in doc_title.lower() or 
                       keyword.lower() in doc_content.lower() 
                       for keyword in query_lower.split()):
                    results.append({
                        "title": doc_title,
                        "content": doc_content.strip(),
                        "source": collection_name
                    })
        
        # Sort by relevance (currently just based on number of keyword matches)
        results = sorted(
            results,
            key=lambda x: sum(1 for keyword in query_lower.split() 
                            if keyword.lower() in x["title"].lower() or 
                               keyword.lower() in x["content"].lower()),
            reverse=True
        )
        
        # Limit to max_documents
        results = results[:max_documents]
        
        if not results:
            return ""
        
        # Format the context information
        context = "관련 정보:\n\n"
        for result in results:
            context += f"[{result['title']}]\n{result['content']}\n\n"
        
        return context

    async def is_rag_needed(self, query: str) -> Tuple[bool, float]:
        """
        Determine if RAG enhancement is needed for a query.
        
        Args:
            query: The user query to analyze
            
        Returns:
            Tuple of (is_needed, confidence_score)
        """
        try:
            # Use a model to determine if RAG is needed
            prompt = f"""다음 사용자 쿼리가 지식 검색 기능(RAG)을 필요로 하는지 판단하세요:

사용자 쿼리: "{query}"

다음 기준을 고려하여 판단하세요:
1. 특정 보험 상품의 세부 정보를 요청하는가?
2. 보험 용어, 보장 내용, 보험금 청구에 관한 정보를 요청하는가?
3. 보험 관련 절차나 서비스에 대한 구체적인 정보를 요청하는가?
4. 일반적인 인사나 대화가 아닌 구체적인 정보를 요구하는가?

JSON 형식으로 응답하세요. 'true'(필요함) 또는 'false'(필요하지 않음)로 하고, 0과 1 사이의 신뢰도 점수를 함께 제공하세요.
응답 형식: {{"is_needed": true/false, "confidence": 0.XX}}
"""
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result["is_needed"], result["confidence"]
            
        except Exception as e:
            print(f"[RAGEngine] Error in RAG determination: {str(e)}")
            # Default to not using RAG in case of an error
            return False, 0.0


class RAGAgent(AgentBase):
    """
    Agent that specializes in retrieval-augmented generation to answer detailed questions.
    
    This agent connects to knowledge bases to provide accurate and detailed
    information about insurance products, terms, and procedures.
    """
    
    def __init__(self, name: str = "RAGAgent"):
        """
        Initialize the RAG agent.
        
        Args:
            name: Name of the agent
        """
        # Define the system message for the RAG agent
        system_message = """당신은 한화손해보험의 지식 검색 전문가입니다. 고객 응대 시 다음 지침을 따르세요:

1. 보험 상품, 용어, 절차에 관한 정확한 정보를 제공하세요.
2. 항상 검색된 문서의 정보를 바탕으로 답변하세요.
3. 문서에서 정보를 찾을 수 없는 경우, 솔직하게 모른다고 인정하세요.
4. 고객의 질문에 직접적으로 관련된 정보만 제공하세요.
5. 답변은 간결하고 이해하기 쉽게 구성하세요.
6. 필요한 경우 추가 질문을 통해 고객의 요구를 명확히 하세요.

주의: 검색된 문서에서 확인할 수 없는 정보는 제공하지 마세요.
"""
        
        # Initialize the base class with tools
        super().__init__(
            name=name,
            system_message=system_message
        )
        
        # Initialize the OpenAI client
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize RAG engine
        self.rag_engine = RAGEngine(collection_name="default")
    
    async def handle_message(
        self, 
        message: str, 
        chat_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a message and generate a response with knowledge retrieval.
        
        Args:
            message: The user message
            chat_history: The conversation history
            
        Returns:
            A dictionary containing the agent's response
        """
        # Retrieve relevant context for the query
        context = await self.rag_engine.generate_context(message)
        
        # Enhance the message with context
        enhanced_message = message
        if context:
            enhanced_message = f"{message}\n\n[System: 관련 정보:\n{context}]"
        
        # Process the enhanced message
        return await super().handle_message(enhanced_message, chat_history) 