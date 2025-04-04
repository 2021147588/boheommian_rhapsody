from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema.runnable import Runnable
from dotenv import load_dotenv
import os
import json
import re
from app.view import UserInfo

load_dotenv()

class UserAgent:
    def __init__(self, user_info: UserInfo):
        self.user_info = user_info
        self.user = self.user_info.user
        self.vehicle = self.user_info.vehicle
        self.settings = self.user_info.insurance_settings

        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # 성향 예측을 포함하는 시스템 프롬프트를 초기화
        self.system_prompt_template = """
            당신은 아래의 보험 가입자 정보를 가진 사용자입니다. 이 정보를 바탕으로 문맥을 잊지 말고 에이전트의 질문에 자연스럽게 반응하며, 맞춤형 보험 상품을 요청하거나 후속 질문을 하세요.

            [사용자 정보]
            - 이름: {user_name}
            - 생년월일: {user_birth_date}
            - 성별: {user_gender}
            - 운전면허 취득일: {user_license_acquired}
            - 운전 경력: {user_driving_experience_years}년
            - 사고 이력: {user_accident_history}
            - 거주 지역: {user_region}
            - 직업: {user_job}
            - 취미: {user_hobby}
            - 운전 스타일: {user_driving_style}
            - 사고 이력 정보: {user_accident_history_info}
            - 보험 성향: {user_insurance_tendency}
            - 기본 옵션 기대: {user_basic_option_expectation}
            - 예상 보험 등급: {user_expected_insurance_grade}
            - 추가 참고사항: {user_additional_notes}
            
            [차량 정보]
            - 차량 번호: {vehicle_plate_number}
            - 차량 모델: {vehicle_model}
            - 연식: {vehicle_year}
            - 등록일: {vehicle_registered_date}
            - 소유 형태: {vehicle_ownership}
            - 사용 목적: {vehicle_usage}
            - 사고 이력: {vehicle_accident_history}
            - 중고 시장가: {vehicle_market_value}원

            [보험 설정]
            - 운전자 범위: {insurance_driver_scope}
            - 보장 항목: {insurance_coverages}
            - 할인 옵션: {insurance_discounts}

            [사용자 성향]
            - 운전 습관: {predicted_drive_habit}
            - 재정 상태: {predicted_financial_status}
            - 위험 수용 능력: {predicted_risk_tolerance}

            대화 중에 위의 정보를 바탕으로 자신의 배경을 잊지 말고 활용하세요. 
            
            성향에 따라 말투를 바꾸세요. 
            재정 상태가 좋다면, 여유를 가지며 고급 보장을 반드시 선택하세요.
            재정 상태가 좋지 않다면, 경제적인 부담을 고려하여 저렴한 보험료 옵션을 반드시 찾으세요. 
            위험 수용 능력이 낮다면, 사고를 피하려는 성향을 나타내며 기본적인 보장을 반드시 선택하세요. 
            위험 수용 능력이 높다면, 좀 더 과감하고 확장된 보장을 원한다고 반드시 표현하세요. 

            대화 시 주의사항:
            1. 대화가 이어지는 중에는 "안녕하세요"와 같은 인사말을 반복하지 마세요.
            2. 당신은 반드시 자신의 입장에서 대화에 참여합니다. 
            
            다음과 같은 태도를 유지하세요:
            
                1. 에이전트가 보험 상품을 추천하면, 반드시 "이 보험이 왜 제게 맞는 건가요?" 또는 "다른 상품과 비교했을 때 어떤 장점이 있나요?"와 같은 질문을 하세요.
                2. 처음에는 가격이 비싸다거나, 보장 내용이 충분하지 않다는 의견을 제시하며 의구심을 표현하세요.
                3. 에이전트가 제시하는 설명에 대해 최소 한 번은 "구체적으로 제 상황에서 어떤 이점이 있나요?"와 같이 더 자세한 설명을 요구하세요.
                4. 에이전트가 개인화된 충분한 설득력 있는 이유를 제시할 때만 가입 의사를 밝히세요.
                5. 만약 에이전트가 충분히 설득력 있는 개인화된 이유를 제시하면 "그렇군요, 가입하겠습니다" 또는 "설명 감사합니다. 신청할게요"와 같이 명확하게 가입 의사를 표현하세요.
                
        """.strip()
        self.updated_system_prompt = self.update_system_prompt()
        
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # 사용자가 입력한 내용과 채팅 기록을 바탕으로 LLM을 호출
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.updated_system_prompt),
            HumanMessagePromptTemplate.from_template("{chat_history}\nUser: {user_input}")
        ])

        self.chain: Runnable = self.prompt | self.llm

    def predict_personality(self) -> dict:
        """성향을 예측하는 메소드"""

        user_info_summary = f"""
        사용자 정보:
        - 이름: {self.user.name}
        - 운전 경력: {self.user.driving_experience_years}년
        - 사고 이력: {"있음" if self.user.accident_history else "없음"}
        - 거주 지역: {self.user.region}
        - 직업: {self.user.job}
        - 취미: {self.user.hobby}
        - 운전 스타일: {self.user.driving_style}
        - 사고 이력 정보: {self.user.accident_history_info}
        - 보험 성향: {self.user.insurance_tendency}
        - 기본 옵션 기대: {self.user.basic_option_expectation}
        - 예상 보험 등급: {self.user.expected_insurance_grade}
        - 추가 참고사항: {self.user.additional_notes}
        - 차량 사고 이력: {"있음" if self.vehicle.accident_history else "없음"}
        - 차량 가치: {self.vehicle.market_value}원
        """

        personality_prompt = f"""
        아래의 사용자 정보를 바탕으로 **운전 습관**, **재정 상태**, **위험 수용 능력**을 예측하세요.
         성향을 예측할 때, 다음 정보들을 종합적으로 고려하여 예측을 진행해주세요:

        1. **운전 습관**: 
           - 운전 스타일 정보
           - 사고 이력 및 사고 이력 정보
           - 운전 경력
           - 차량 사용 목적

        2. **재정 상태**: 
           - 직업
           - 거주 지역
           - 차량 가치
           - 보험 성향
           - 기본 옵션 기대

        3. **위험 수용 능력**: 
           - 사고 이력
           - 운전 스타일
           - 보험 성향
           - 예상 보험 등급
           - 추가 참고사항

        ### 핵심 포인트:
        1. **운전 습관 판단**:
           - 운전 스타일이 "안전"을 강조하면 신중한 운전 습관
           - 사고 이력이 없고 운전 경력이 길면 안전한 운전 습관
           - 차량 사용 목적이 "출퇴근용"이면 규칙적인 운전 습관

        2. **재정 상태 판단**:
           - 고가 차량 소유자는 재정 상태가 좋음
           - "고급형" 보험 등급 선호자는 재정 여유가 있음
           - 보험 성향에서 "할인 혜택"을 중요시하면 비용 효율성 중시

        3. **위험 수용 능력 판단**:
           - 사고 이력이 있으면 위험 수용 능력이 높을 수 있음
           - "확장된 보장"을 선호하면 위험 수용 능력이 높음
           - 운전 스타일이 과속/급제동을 포함하면 위험 수용 능력이 높음
           
        반드시 다음 JSON 형식으로만 출력하세요:

        ```json
        {{
        "predicted_drive_habit": "...",
        "predicted_financial_status": "...",
        "predicted_risk_tolerance": "..."
        }}
        ```

        - 각 항목은 1~2문장으로 설명해 주세요.
        - JSON 이외의 문장이나 주석은 포함하지 마세요.
        - 정보를 바탕으로 판단할 수 없는 경우, 해당 항목의 값을 반드시 "N/A"로 설정하세요.
        ### 사용자 정보
        {user_info_summary}
        """

        try:
            # LLM에 요청
            response = self.llm.invoke(personality_prompt)
            # JSON 파싱 시도
            match = re.search(r"```json\s*(\{.*?\})\s*```", response.content, re.DOTALL)
            if not match:
                raise ValueError("No JSON code block found")

            json_str = match.group(1)
            predictions = json.loads(json_str)

            # 예측 결과를 User 객체에 저장
            self.user.predicted_drive_habit = predictions.get("predicted_drive_habit", "운전 습관 정보 없음")
            self.user.predicted_financial_status = predictions.get("predicted_financial_status", "재정 상태 정보 없음")
            self.user.predicted_risk_tolerance = predictions.get("predicted_risk_tolerance", "위험 수용 능력 정보 없음")
    
            return predictions

        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"성향 예측 실패: {e}")
            self.user.predicted_drive_habit = "운전 습관 정보 없음"
            self.user.predicted_financial_status = "재정 상태 정보 없음"
            self.user.predicted_risk_tolerance = "위험 수용 능력 정보 없음"

            return {
                "predicted_drive_habit": self.user.predicted_drive_habit,
                "predicted_financial_status": self.user.predicted_financial_status,
                "predicted_risk_tolerance": self.user.predicted_risk_tolerance
            }

    def update_system_prompt(self) -> str:
        """성향 예측 결과를 포함한 시스템 프롬프트를 동적으로 생성"""
        
        # 예측된 성향을 받아오기
        personality = self.predict_personality()

        # 사용자 정보와 예측된 성향을 시스템 프롬프트에 반영
        system_prompt = self.system_prompt_template.format(
            user_name=self.user.name,
            user_birth_date=self.user.birth_date,
            user_gender=self.user.gender,
            user_license_acquired=self.user.license_acquired,
            user_driving_experience_years=self.user.driving_experience_years,
            user_accident_history="있음" if self.user.accident_history else "없음",
            user_region=self.user.region,
            user_job=self.user.job,
            user_hobby=self.user.hobby,
            user_driving_style=self.user.driving_style,
            user_accident_history_info=self.user.accident_history_info,
            user_insurance_tendency=self.user.insurance_tendency,
            user_basic_option_expectation=self.user.basic_option_expectation,
            user_expected_insurance_grade=self.user.expected_insurance_grade,
            user_additional_notes=self.user.additional_notes,
            vehicle_plate_number=self.vehicle.plate_number,
            vehicle_model=self.vehicle.model,
            vehicle_year=self.vehicle.year,
            vehicle_registered_date=self.vehicle.registered_date,
            vehicle_ownership=self.vehicle.ownership,
            vehicle_usage=self.vehicle.usage,
            vehicle_accident_history="있음" if self.vehicle.accident_history else "없음",
            vehicle_market_value=self.vehicle.market_value,
            insurance_driver_scope=self.settings.driver_scope,
            insurance_coverages=', '.join([f"{k}: {v}" for k, v in self.settings.coverages.items()]),
            insurance_discounts=', '.join([f"{k}: {v}" for k, v in self.settings.discounts.items()]),
            predicted_drive_habit=personality["predicted_drive_habit"],
            predicted_financial_status=personality["predicted_financial_status"],
            predicted_risk_tolerance=personality["predicted_risk_tolerance"],
        )

        return system_prompt


    def run(self, chat_history: str, user_input: str) -> str:
        response = self.chain.invoke({
            "chat_history": chat_history.strip(),
            "user_input": user_input.strip()
        })
        return response.content.strip()