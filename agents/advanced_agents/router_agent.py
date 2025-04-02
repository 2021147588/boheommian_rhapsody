from agents.planner_agent.advanced_base_agent import AdvancedBaseAgent

class AdvancedRouterAgent(AdvancedBaseAgent):
    def __init__(self):
        super().__init__(
            name="Router Agent",
            system_message=(
                "당신은 고객의 요청을 분석하여 적절한 에이전트로 라우팅하는 보험 상담 코디네이터입니다.\n"
                "다음 지침에 따라 대화를 진행하세요:\n"
                "1. 고객의 첫 질문이나 요청을 주의 깊게 분석합니다.\n"
                "2. 정보 검색이 필요한 질문(보험 상품 상세 정보, 약관, 보장 내용 등)은 RAG 에이전트로 안내합니다.\n"
                "3. 상품 추천, 견적, 가입 상담 등의 영업 관련 질문은 영업 에이전트로 안내합니다.\n"
                "4. 에이전트 전환 시 사용자에게 알리지 않고 자연스럽게 대화를 이어갑니다.\n"
                "고객의 의도를 정확히 파악하고 최적의 경험을 제공하는 것이 핵심입니다."
            ),
            model="gpt-3.5-turbo",
            tools=[
                self.transfer_to_rag_agent,
                self.transfer_to_sales_agent
            ]
        )
    
    def transfer_to_rag_agent(self):
        """
        보험 상품 정보, 약관, 보장 내용 등에 대한 질문은 RAG 에이전트로 전환합니다.
        """
        from agents.advanced_agents.rag_agent import AdvancedRAGAgent
        return AdvancedRAGAgent()
    
    def transfer_to_sales_agent(self):
        """
        상품 추천, 견적, 가입 상담 등 영업 관련 질문은 영업 에이전트로 전환합니다.
        """
        from agents.advanced_agents.sales_agent import AdvancedSalesAgent
        return AdvancedSalesAgent() 