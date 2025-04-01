from autogen import ConversableAgent
import os
from dotenv import load_dotenv
load_dotenv()
class UserAgent:
    def __init__(self, user_info):
        # 여기에 알아서 user info 추가하길..
        system_prompt = (
                "당신은 보험에 관심이 많은 30대 직장인입니다. "
                "암보험, 실손보험, 자동차보험 등 다양한 보험 상품에 대해 궁금해하며, "
                "에이전트가 답변해주면 그 내용을 이해하려고 후속 질문을 하거나, "
                "자신의 상황(예: 가족력, 예산, 나이 등)에 맞는 맞춤형 상품을 요청합니다. "
                "대화를 자연스럽게 이어가세요."
            )
        
        self.agent = ConversableAgent(
            name="user",
            system_message=system_prompt,
            llm_config={
                "config_list": [
                    {
                        "model": "gpt-3.5-turbo",
                        "api_key": os.getenv("OPENAI_API_KEY")
                    }
                ]
            }
        )

    def get_agent(self):
        return self.agent