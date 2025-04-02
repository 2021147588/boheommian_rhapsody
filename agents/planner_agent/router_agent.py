from agents.planner_agent.base_agent import BaseAgent
from agents.planner_agent.sales_agent import SalesAgent
from agents.planner_agent.rag_agent import RAGAgent

class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RouterAgent",
            system_message="당신은 고객 요청을 분석하여 적절한 에이전트로 라우팅하는 역할을 합니다. "
            "정보 검색이 필요한 질문은 RAG 에이전트로, 상품 추천이나 판매 관련 질문은 영업 에이전트로 안내하세요. "
            "고객의 의도를 파악하고 가장 적합한 에이전트를 선택하는 것이 중요합니다."
        )

        self.sales_agent = SalesAgent()
        self.rag_agent = RAGAgent()
        
        # 라우팅 함수 설정
        self.agent.llm_config = {
            "functions": [
                self.transfer_to_sales_agent,
                self.transfer_to_rag_agent
            ]
        }
    
    def transfer_to_sales_agent(self):
        """
        고객이 상품 추천, 견적, 구매 상담 등 영업 관련 질문을 할 때 호출합니다.
        """
        return self.sales_agent.get_agent()
    
    def transfer_to_rag_agent(self):
        """
        고객이 보험 상품 정보, 보장 내용, 약관 등에 대한 구체적인 정보를 요청할 때 호출합니다.
        """
        return self.rag_agent.get_agent() 