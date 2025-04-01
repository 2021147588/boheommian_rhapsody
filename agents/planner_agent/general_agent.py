from agents.planner_agent.base_agent import BaseAgent

class GeneralAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="GeneralAssistant",
            system_message="당신은 일반적인 질문에 친절하게 답변하는 AI입니다."
        )
