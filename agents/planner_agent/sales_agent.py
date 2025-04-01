from agents.planner_agent.base_agent import BaseAgent


class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SalesAssistant",
            system_message="당신은 보험 관련 상품을 제안하고 고객의 니즈를 파악하는 세일즈 전문가입니다."
        )
