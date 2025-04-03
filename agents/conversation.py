from agents.advanced_orchestrator import AdvancedOrchestrator
from agents.user_agent.user_agent import UserAgent
from backend.view import *
import json

class AgentConversation:
    def __init__(self, user_info: UserInfo, max_turns: int = 2):
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
        
        # 에이전트 활용 로그 추가
        active_agents_log = []
        
        for turn in range(self.max_turns):
            print(f"\n🔁 [Turn {turn+1}]")

            # 현재 활성 에이전트 확인 및 로깅
            current_agent_name = getattr(self.orchestrator.active_agent, 'name', 'Router Agent') if self.orchestrator.active_agent else 'Router Agent'
            active_agents_log.append(f"Turn {turn+1}: {current_agent_name}")
            print(f"[Active Agent]: {current_agent_name}")

            # 1. Orchestrator가 응답
            orchestrator_response = self.orchestrator.run_with_history(
                self.chat_history,
                self.chat_history + user_message
            )
            print(f"[Orchestrator]: {orchestrator_response}")
            self.chat_history += f"{orchestrator_response}\nUser: "
            self.chat_log.append({
                "role": "orchestrator", 
                "content": orchestrator_response,
                "agent": current_agent_name  # 에이전트 정보 추가
            })

            # 응답 후 에이전트 변경 확인 및 로깅 (핸드오프 발생 시)
            new_agent_name = getattr(self.orchestrator.active_agent, 'name', 'Router Agent') if self.orchestrator.active_agent else 'Router Agent'
            if new_agent_name != current_agent_name:
                print(f"[Agent Handoff]: {current_agent_name} -> {new_agent_name}")
                active_agents_log.append(f"Handoff: {current_agent_name} -> {new_agent_name}")

            # 2. UserAgent가 응답
            user_response = self.user_agent.run(self.chat_history, orchestrator_response)
            print(f"[User] {user_response}")
            self.chat_log.append({"role": "user", "content": user_response})
            self.chat_history += f"{user_response}\nOrchestrator:"

            user_message = user_response  # 다음 턴 입력
        
        # 에이전트 활용 로그 요약 출력
        print("\n=== 에이전트 활용 로그 ===")
        for log_entry in active_agents_log:
            print(log_entry)
        
        # 에이전트 활용 로그를 채팅 로그에 추가
        self.chat_log.append({"role": "system", "content": "Agent Usage Summary", "agent_log": active_agents_log})

if __name__ == "__main__":
    user_info_json_path = "C:/Users/woorifill hafs.kr/Documents/GitHub/boheommian_rhapsody/agents/person.json"
    with open(user_info_json_path, "r", encoding="utf-8") as file:
        user_info_list = json.load(file)
    
    total_chat_log = []
    for user_info_dict in user_info_list:
        user_info = UserInfo(**user_info_dict)
        conversation = AgentConversation(user_info)
        conversation.simulate_conversation()
        
        # 대화 로그 저장
        chat_data = {
            "conversation": conversation.chat_log
        }
        total_chat_log.append(chat_data)
    
    with open("chat_log.json", "w", encoding='utf-8') as file:
        json.dump(total_chat_log, file, ensure_ascii=False, indent=4)

    

    