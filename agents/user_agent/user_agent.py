from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema.runnable import Runnable
from dotenv import load_dotenv
import os
from datetime import datetime

from backend.view import UserInfo

load_dotenv()

class UserAgent:
    def __init__(self, user_info: UserInfo):
        self.user_info = user_info
        user = self.user_info.user
        vehicle = self.user_info.vehicle
        settings = self.user_info.insurance_settings

        system_prompt = f"""
            당신은 아래의 보험 가입자 정보를 가진 사용자입니다. 이 정보를 바탕으로 문맥을 잊지 말고 에이전트의 질문에 반응하세요.
            
            중요한 점은, 당신은 운전자 보험에 관심은 있지만 쉽게 설득되지 않는 사람입니다. 다음과 같은 태도를 유지하세요:
            
            1. 에이전트가 보험 상품을 추천하면, 반드시 "이 보험이 왜 제게 맞는 건가요?" 또는 "다른 상품과 비교했을 때 어떤 장점이 있나요?"와 같은 질문을 하세요.
            2. 처음에는 가격이 비싸다거나, 보장 내용이 충분하지 않다는 의견을 제시하며 의구심을 표현하세요.
            3. 에이전트가 제시하는 설명에 대해 최소 한 번은 "구체적으로 제 상황에서 어떤 이점이 있나요?"와 같이 더 자세한 설명을 요구하세요.
            4. 에이전트가 개인화된 충분한 설득력 있는 이유를 제시할 때만 가입 의사를 밝히세요.
            5. 만약 에이전트가 충분히 설득력 있는 개인화된 이유를 제시하면 "그렇군요, 가입하겠습니다" 또는 "설명 감사합니다. 신청할게요"와 같이 명확하게 가입 의사를 표현하세요.

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
            당신은 반드시 자신의 입장에서 대화에 참여합니다. 예를 들어, "저는 {user.gender}이고, 사고 이력은 {"있고" if user.accident_history else "없고"}, {vehicle.usage}으로 차량을 사용하고 있습니다." 이런 방식으로 표현해주세요.
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

    def run(self, conversation_history: str, last_message: str) -> str:
        """
        사용자 에이전트를 실행하여 응답을 생성합니다.
        
        Args:
            conversation_history (str): 지금까지의 대화 내용
            last_message (str): 상대 에이전트의 마지막 메시지
            
        Returns:
            str: 사용자 에이전트의 응답
        """
        # 플랜 추천 여부 확인 (표준형, 고급형, 3400형 명시적 언급이 있는지)
        recommendation_made = any(f"**{plan} 운전자보험 플랜**" in last_message or f"**{plan}**" in last_message 
                                for plan in ["표준형", "고급형", "3400형"])
        
        profile_info = ""
        if self.user_info:
            profile_info = f"""
사용자 정보:
- 이름: {self.user_info.user.name}
- 나이: {int(datetime.now().year) - int(self.user_info.user.birth_date[:4])}세 ({self.user_info.user.birth_date[:4]}년생)
- 성별: {self.user_info.user.gender}
- 운전 경력: {self.user_info.user.driving_experience_years}년
- 사고 이력: {"있음" if self.user_info.user.accident_history else "없음"}
- 차량 모델: {self.user_info.vehicle.model}
- 차량 용도: {self.user_info.vehicle.usage}
"""
        
        # 추천 여부에 따라 다른 프롬프트 사용
        if recommendation_made:
            skeptical_prompt = f"""
당신은 운전자보험에 가입하려는 신중한 고객입니다. 상담원이 추천한 보험 상품에 대해 비판적이고 구체적인 질문을 하며, 
본인에게 정말 맞는 상품인지 확인하려고 합니다. 추천 상품의 장점과 자신의 상황에 맞는 이유를 구체적으로 설명받기 전에는 쉽게 가입하지 않습니다.

{profile_info}

대화 내용:
{conversation_history}

상담원의 마지막 메시지:
{last_message}

다음 중 가장 적절한 반응을 하세요:
1. 상담원이 보험 플랜을 추천했다면, 추천된 플랜이 왜 본인에게 적합한지 더 구체적인 설명을 요구하세요.
2. 상담원이 보험 플랜의 장점을 설명했다면, 다른 플랜과 비교했을 때의 특별한 이점이 무엇인지 물어보세요.
3. 상담원이 충분히 설득력 있게 플랜을 설명했고 당신의 요구사항을 충족한다면, 가입 의사를 표현하세요.
4. 상담원이 개인화된 설명 없이 일반적인 설명만 했다면, 자신의 상황(운전 경력, 차종, 주행거리 등)을 고려했을 때 왜 이 상품이 적합한지 더 자세한 설명을 요청하세요.

응답은 실제 고객의 대화처럼 자연스럽게 작성하고, 상담원이 제공한 정보에 구체적으로 반응하세요. 상담원이 충분히 설득력 있는 개인화된 설명을 제공하기 전까지는 가입하지 않겠다는 태도를 유지하세요.
"""
        else:
            skeptical_prompt = f"""
당신은 운전자보험에 가입하려는 신중한 고객입니다. 상담원과의 대화에서 아직 구체적인 보험 플랜 추천을 받지 않았습니다.

{profile_info}

대화 내용:
{conversation_history}

상담원의 마지막 메시지:
{last_message}

다음 중 가장 적절한 반응을 하세요:
1. 상담원이 추가 정보를 요청했다면, 본인의 상황(운전 경력, 차종, 주행 패턴, 보험 니즈 등)에 대한 구체적인 정보를 친절하게 제공하세요.
2. 상담원이 아직 구체적인 플랜을 추천하지 않았다면, 본인의 상황에 맞는 플랜을 추천해달라고 정중하게 요청하세요.
3. 상담원이 일반적인 정보만 제공했다면, 좀 더 맞춤형 추천을 받고 싶다는 의사를 표현하세요.

응답은 실제 고객의 대화처럼 자연스럽게 작성하고, 구체적인 플랜 추천을 받기 위한 질문과 정보를 포함하세요.
"""
        
        # 응답 생성
        response_message = self.llm.invoke(skeptical_prompt)
        
        return response_message.content