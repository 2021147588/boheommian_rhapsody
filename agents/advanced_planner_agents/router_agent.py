from agents.advanced_planner_agents.advanced_base_agent import AdvancedBaseAgent
from agents.advanced_planner_agents.rag_agent import AdvancedRAGAgent
from agents.advanced_planner_agents.recommendation_agent import AdvancedRecommendationAgent
from agents.advanced_planner_agents.sales_agent import AdvancedSalesAgent
from agents.advanced_planner_agents.graph_rag_agent import GraphRAGAgent

class AdvancedRouterAgent(AdvancedBaseAgent):
    def __init__(self):
        super().__init__(
            name="Router Agent",
            system_message=(
                "당신은 고객의 요청을 분석하여 적절한 에이전트로 라우팅하는 보험 상담 코디네이터입니다.\n"
                "다음 지침에 따라 대화를 진행하세요:\n"
                "1. 고객의 첫 질문이나 요청을 주의 깊게 분석합니다.\n"
                "2. 정보 검색이 필요한 질문(보험 상품 상세 정보, 약관, 보장 내용 등)은 RAG 에이전트로 안내합니다.\n"
                "3. 상품 비교나 추천 요청은 추천 에이전트로 안내합니다.\n"
                "4. 가입 상담, 구매 절차, 서류 안내 등 영업 관련 질문은 영업 에이전트로 안내합니다.\n"
                "5. 에이전트를 전환할 때는 사용자가 시스템 구조를 인식하지 못하도록 자연스럽게 이어가세요.\n" 
                 "예를 들어, 'RAG 에이전트로 넘기겠습니다 또는 '추천 에이전트를 호출합니다와 같은 표현은 절대 사용하지 마세요.\n" 
                "대신, 사용자의 질문에 맞는 정보나 설명을 곧바로 제공하거나, 관련 내용을 안내하는 방식으로 응답을 이어가세요."
                            ),
            model="gpt-4o-mini",
            tools=[
                self.transfer_to_rag_agent,
                self.transfer_to_recommendation_agent,
                self.transfer_to_sales_agent
            ]
        )
    
    def transfer_to_rag_agent(self):
        """
        보험 상품 정보, 약관, 보장 내용 등에 대한 질문은 RAG 에이전트로 전환합니다.
        """
        return GraphRAGAgent()
    
    def transfer_to_recommendation_agent(self):
        """
        상품 추천, 비교 분석 등의 질문은 추천 에이전트로 전환합니다.
        """
        return AdvancedRecommendationAgent()
    
    def transfer_to_sales_agent(self):
        """
        상품 가입, 구매 절차, 상담 예약 등 영업 관련 질문은 영업 에이전트로 전환합니다.
        """
        return AdvancedSalesAgent() 