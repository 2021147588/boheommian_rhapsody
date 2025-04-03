from agents.advanced_orchestrator import AdvancedOrchestrator
from agents.user_agent.user_agent import UserAgent
from backend.view import *
import json

class AgentConversation:
    def __init__(self, user_info: UserInfo, max_turns: int = 5):
        self.user_agent = UserAgent(user_info)
        self.orchestrator = AdvancedOrchestrator()
        self.chat_log = []
        self.max_turns = max_turns
        self.chat_history = ""  # 문자열 형태로 유지

        # 사용자 정보 요약
        self.user_info_summary = f"""
            사용자 정보:
            - 이름: {user_info.user.name}
            - 나이: {user_info.user.birth_date[:4]}
            - 성별: {user_info.user.gender}
            - 운전 경력: {user_info.user.driving_experience_years}년
            - 사고 이력: {"있음" if user_info.user.accident_history else "없음"}
            - 차량 모델: {user_info.vehicle.model}
            - 사용 목적: {user_info.vehicle.usage}
        """
                    
    def simulate_conversation(self, initial_input: str = "운전자 보험 추천해주세요."):
        print("=== 에이전트 간 자동 대화 시뮬레이션 시작 ===")
        user_message = initial_input
        self.chat_history += f"User: {initial_input}\nOrchestrator: "
        self.chat_log.append({"role": "user", "content": user_message})

        # 매번 사용자 정보를 대화 흐름에 포함시켜서 대화가 지속적으로 이어지도록
        self.chat_history = self.user_info_summary + "\n" + self.chat_history
        
        for turn in range(self.max_turns):
            print(f"\n🔁 [Turn {turn+1}]")

            # 1. Orchestrator가 응답
            orchestrator_response = self.orchestrator.run_with_history(
                self.chat_history,
                user_message
            )
            print(f"[Orchestrator]: {orchestrator_response}")
            self.chat_history += f"{orchestrator_response}\nUser: "
            self.chat_log.append({"role": "orchestrator", "content": orchestrator_response})

            # 2. UserAgent가 응답
            user_response = self.user_agent.run(self.chat_history, orchestrator_response)
            print(f"[User] {user_response}")
            self.chat_log.append({"role": "user", "content": user_response})
            self.chat_history += f"{user_response}\nOrchestrator:"

            user_message = user_response  # 다음 턴 입력

if __name__ == "__main__":
    user_info_json_path = "person.json"
    with open(user_info_json_path, "r", encoding="utf-8") as file:
        user_info_list = json.load(file)
    
    for user_info in user_info_list:
        conversation = AgentConversation(user_info)
        conversation.simulate_conversation()
        
        # 대화 로그 저장
        chat_data = {
            "conversation": conversation.chat_log
        }
        # 모든 대화 로그를 하나의 파일에 저장
        with open("chat_log.json", "w", encoding='utf-8') as file:
            json.dump(chat_data, file, ensure_ascii=False, indent=4)

    