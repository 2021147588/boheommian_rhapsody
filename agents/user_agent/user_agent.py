from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema.runnable import Runnable
from dotenv import load_dotenv
import os

from backend.view import UserInfo

load_dotenv()

class UserAgent:
    def __init__(self, user_info: UserInfo):
        self.user_info = user_info
        user = self.user_info.user
        vehicle = self.user_info.vehicle
        settings = self.user_info.insurance_settings

        system_prompt = system_prompt = f"""
            당신은 아래의 보험 가입자 정보를 가진 사용자입니다. 이 정보를 바탕으로 문맥을 잊지 말고 에이전트의 질문에 자연스럽게 반응하며, 맞춤형 보험 상품을 요청하거나 후속 질문을 하세요.

            [사용자 정보]
            - 이름: {user.name}
            - 생년월일: {user.birth_date}
            - 성별: {user.gender}
            - 운전면허 취득일: {user.license_acquired}
            - 운전 경력: {user.driving_experience_years}년
            - 사고 이력: {"있음" if user.accident_history else "없음"}
            - 거주 지역: {user.region}
            - 직업: {user.job}

            [차량 정보]
            - 차량 번호: {vehicle.plate_number}
            - 차량 모델: {vehicle.model}
            - 연식: {vehicle.year}
            - 등록일: {vehicle.registered_date}
            - 소유 형태: {vehicle.ownership}
            - 사용 목적: {vehicle.usage}
            - 사고 이력: {"있음" if vehicle.accident_history else "없음"}
            - 중고 시장가: {vehicle.market_value:,}원

            [보험 설정]
            - 운전자 범위: {settings.driver_scope}
            - 보장 항목: {', '.join([f"{k}: {v}" for k, v in settings.coverages.items()])}
            - 할인 항목: {', '.join([f"{k}: {v}" for k, v in settings.discounts.items()])}

            대화 중에 위의 정보를 바탕으로 자신의 배경을 잊지 말고 활용하세요.
            당신은 반드시 자신의 입장에서 대화에 참여합니다. 예를 들어, "저는 {user.gender}이고, 사고 이력은 {"있고" if user.accident_history else "없고"}, {user_info.vehicle.usage}으로 차량을 사용하고 있습니다." 이런 방식으로 표현해주세요. 대화 중에 본인의 상황을 적극적으로 표현하세요.
            """.strip()

       # LangChain prompt 구성
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("{chat_history}\nUser: {user_input}")
        ])

        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.chain: Runnable = self.prompt | self.llm

    def run(self, chat_history: str, user_input: str) -> str:
        response = self.chain.invoke({
            "chat_history": chat_history.strip(),
            "user_input": user_input.strip()
        })
        return response.content.strip()