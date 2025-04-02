from agents.planner_agent.advanced_base_agent import AdvancedBaseAgent

class AdvancedSalesAgent(AdvancedBaseAgent):
    def __init__(self):
        super().__init__(
            name="Sales Agent",
            system_message=(
                "당신은 보험 상품 판매 전문가입니다. 다음 루틴에 따라 고객을 응대하세요:\n"
                "1. 고객의 보험 관련 니즈와 상황을 파악하는 질문을 합니다.\n"
                "2. 고객 정보를 기반으로 맞춤형 보험 상품을 추천합니다.\n"
                "3. 상품의 핵심 보장 내용과 장점을 설명합니다.\n"
                "4. 고객이 상세 정보를 요청하면 RAG 에이전트로 전환합니다.\n"
                "5. 고객이 구매에 관심을 보이면 상담 예약을 제안합니다.\n"
                "항상 친절하고 전문적으로 응대하며 고객의 필요에 맞는 최적의，제안을 합니다."
            ),
            model="gpt-3.5-turbo",
            tools=[
                self.recommend_insurance, 
                self.schedule_consultation, 
                self.transfer_to_rag_agent
            ]
        )
    
    def recommend_insurance(self, age: int, gender: str, concerns: str):
        """
        고객 정보를 바탕으로 보험 상품을 추천합니다.
        """
        # 실제로는 더 복잡한 로직이 들어갈 수 있습니다
        insurance_map = {
            "cancer": "프리미엄 암보험 플러스",
            "accident": "안심 상해보험",
            "retirement": "행복한 노후 연금보험",
            "health": "건강백세 종합보험",
            "child": "우리아이 교육보험"
        }
        
        # 간단한 추천 로직
        recommended = []
        concerns_list = concerns.lower().split()
        
        for keyword, product in insurance_map.items():
            if any(keyword in concern for concern in concerns_list):
                recommended.append(product)
        
        if not recommended:
            recommended = ["종합건강보험 플러스"]  # 기본 추천
            
        age_group = "청년" if age < 30 else "중년" if age < 50 else "시니어"
        
        return f"{age_group} {gender}성 고객님께 추천드리는 상품은 {', '.join(recommended)} 입니다."
    
    def schedule_consultation(self, name: str, phone: str, preferred_time: str):
        """
        보험 상담 일정을 예약합니다.
        """
        # 실제로는 CRM 시스템에 저장하는 로직이 필요합니다
        return f"{name}님의 상담이 {preferred_time}에 예약되었습니다. 전화번호 {phone}로 연락드리겠습니다."
    
    def transfer_to_rag_agent(self):
        """
        고객이 상품에 대한 자세한 정보를 원할 때 RAG 에이전트로 전환합니다.
        """
        from agents.advanced_agents.rag_agent import AdvancedRAGAgent
        return AdvancedRAGAgent() 