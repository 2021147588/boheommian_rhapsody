from agents.user_agent.user_agent import UserAgent
from agents.planner_agent.rag_agent import RAGAgent
from agents.planner_agent.sales_agent import SalesAgent
from agents.planner_agent.general_agent import GeneralAgent
from utils.logger import  setup_logger
from backend.view import UserInfo
logger = setup_logger()

class AgentConversationSystem:
    def __init__(self, user_info: UserInfo):
        self.user_agent = UserAgent(user_info=user_info).get_agent()
        self.rag_agent = RAGAgent().get_agent()
        self.general_agent = GeneralAgent().get_agent()
        self.sales_agent = SalesAgent().get_agent()
        self.conversation_log = []  

    def _select_agent(self, message: str):
        if message is None:  # 수정된 부분
            return None
        message = message.lower()
        if any(keyword in message for keyword in ["문서", "보장", "계약", "약관"]):
            return self.rag_agent
        elif any(keyword in message for keyword in ["가입", "상품", "추천", "세일"]):
            return self.sales_agent
        else:
            return self.general_agent

    def run_simulation(self, message: str, rounds: int = 5):
        current_agent = self._select_agent(message)
        self.user_agent.send(message, current_agent)
        self.conversation_log.append({"speaker": "user", "message": message})

        for _ in range(rounds):
            # assistant 응답 생성
            reply = current_agent.generate_reply(sender=self.user_agent)
            print(f"{current_agent.name}: {reply}")
            self.conversation_log.append({"speaker": current_agent.name, "message": reply})

            # assistant 응답을 user에게 전달
            self.user_agent.send(reply, current_agent)

            # user가 assistant 응답에 대해 follow-up 질문 생성
            user_followup = self.user_agent.generate_reply(sender=current_agent)
            print(f"{self.user_agent.name}: {user_followup}")
            self.conversation_log.append({"speaker": self.user_agent.name, "message": user_followup})

            # 다음 라운드에 적절한 agent 재선택
            current_agent = self._select_agent(user_followup)
            if current_agent == None:
                return 
            current_agent.send(user_followup, self.user_agent)

    def get_script(self):
        return self.conversation_log

if __name__ == "__main__":
    user_info = ''
    system = AgentConversationSystem(user_info)
    
    system.run_simulation("암보험 가입 상품 추천해줘")