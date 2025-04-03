"""
프로필 에이전트 - 사용자 프로필 정보 추출 및 관리

이 에이전트는 대화에서 프로필 정보를 추출하고
다른 에이전트가 접근할 수 있는 중앙 집중식 사용자 프로필을 관리하는 데 특화되어 있습니다.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from openai import AsyncOpenAI
from dotenv import load_dotenv

from agents.core.agent_base import AgentBase
from agents.core.insurance_profile import InsuranceProfile

# 환경 변수 로드
load_dotenv()

class ProfileAgent(AgentBase):
    """
    사용자 프로필 정보 추출 및 관리를 담당하는 에이전트.
    
    이 에이전트는 대화 기록을 분석하여 사용자 프로필 데이터를 추출하고
    다른 에이전트와 공유할 수 있는 중앙 집중식 프로필을 유지합니다.
    """
    
    def __init__(self, name: str = "ProfileAgent"):
        """
        프로필 에이전트를 초기화합니다.
        
        인자:
            name: 에이전트 이름
        """
        # 프로필 에이전트의 시스템 메시지 정의
        system_message = """당신은 사용자와의 대화에서 개인 정보를 추출하는 프로필 관리 에이전트입니다.
프로필 정보 추출 및 관리가 주요 역할이며, 다른 에이전트들이 사용자와 더 효과적으로 상호작용할 수 있도록 돕습니다.
개인정보 보호에 주의하며, 명시적으로 언급된 정보만 수집합니다.
"""
        
        # 기본 클래스 초기화
        super().__init__(
            name=name,
            system_message=system_message,
            tools=[
                self.extract_profile_info,
                self.get_profile_summary,
                self.reset_profile
            ]
        )
        
        # OpenAI 클라이언트 초기화
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # 사용자 프로필 초기화
        self.user_profile = InsuranceProfile()
    
    async def extract_profile_info(self, conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        대화 기록에서 프로필 정보를 추출합니다.
        
        인자:
            conversation_history: 분석할 대화 기록
            
        반환값:
            추출된 프로필 정보의 JSON 문자열
        """
        # 제공된 대화 기록이 없으면 저장된 기록 사용
        if conversation_history is None:
            raise ValueError("Conversation history is required")
        
        # 대화 기록에서 사용자 메시지 추출
        user_messages = [msg["content"] for msg in conversation_history 
                         if msg.get("role") == "user" and "content" in msg]
        
        # 메시지를 하나의 문자열로 결합
        combined_messages = "\n".join(user_messages)
        
        # 추출을 위한 프롬프트 생성
        prompt = f"""
대화 기록에서 사용자에 관한 프로필 정보를 추출하세요. 명시적으로 언급된 정보만 추출하고, 추측하지 마세요.
추출한 정보는 JSON 형식으로 반환하세요.

대화 기록:
{combined_messages}

추출할 정보 필드:
- name: 고객 이름
- age: 나이 (숫자만)
- gender: 성별 (남성/여성)
- occupation: 직업
- driving_experience: 운전 경력 (년 수)
- vehicle_type: 차량 종류 (승용차/SUV/트럭 등)
- annual_mileage: 연간 주행거리 (숫자만, km)
- accident_history: 사고 이력 (배열)
- traffic_violations: 교통법규 위반 이력 (배열)
- commute_distance: 출퇴근 거리 (숫자만, km)
- main_driving_area: 주 운전지역 (도심/고속도로/시외 등)
- current_insurance: 현재 자동차보험 가입 여부 (true/false)
- current_driver_insurance: 현재 운전자보험 가입 여부 (true/false)
- budget_monthly: 보험료 예산 (숫자만, 원)
- coverage_preference: 보장범위 선호 (최소/일반/프리미엄)
- priority_coverage: 우선적으로 원하는 보장 (배열)
- pain_points: 고객이 언급한 운전 관련 우려사항 (배열)
- inquiry_products: 고객이 문의한 보험 상품 (배열)
- preferred_contact_method: 선호하는 연락 방식
- family_info: 가족 구성원 정보
- hobby: 취미 활동
- health_condition: 건강 상태

JSON 형식으로 추출한 정보만 반환하세요. 추출할 수 없는 정보는 해당 필드를 포함하지 마세요.
"""
        
        try:
            # OpenAI API 호출
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            # 응답 파싱
            content = response.choices[0].message.content
            extracted_info = json.loads(content)
            
            # 숫자 및 불리언 필드 처리
            self._process_extracted_fields(extracted_info)
            
            # 사용자 프로필 업데이트
            self._update_profile(extracted_info)
            
            # 추출된 정보를 JSON 문자열로 반환
            return json.dumps(extracted_info, ensure_ascii=False)
            
        except Exception as e:
            print(f"[ProfileAgent] Error extracting profile info: {str(e)}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)
    
    def _process_extracted_fields(self, extracted_info: Dict[str, Any]) -> None:
        """
        추출된 필드를 처리하여 올바른 데이터 타입을 보장합니다.
        
        인자:
            extracted_info: 추출된 프로필 정보
        """
        # 숫자 필드 처리
        for num_field in ['age', 'driving_experience', 'annual_mileage', 'commute_distance', 'budget_monthly']:
            if num_field in extracted_info and isinstance(extracted_info[num_field], str):
                try:
                    # 문자열에서 숫자만 추출
                    extracted_info[num_field] = int(''.join(filter(str.isdigit, extracted_info[num_field])))
                except ValueError:
                    pass
        
        # 불리언 필드 처리
        for bool_field in ['current_insurance', 'current_driver_insurance']:
            if bool_field in extracted_info and isinstance(extracted_info[bool_field], str):
                extracted_info[bool_field] = extracted_info[bool_field].lower() in ['true', 'yes', '예', '네', '가입']
    
    def _update_profile(self, extracted_info: Dict[str, Any]) -> None:
        """
        추출된 정보로 사용자 프로필을 업데이트합니다.
        
        인자:
            extracted_info: 추출된 프로필 정보
        """
        if extracted_info:
            # print(f"[ProfileAgent] Extracted profile fields: {list(extracted_info.keys())}")
            self.user_profile.update(extracted_info)
    
    async def update_profile(self, conversation_history: List[Dict[str, Any]]) -> str:
        """
        대화 기록을 기반으로 사용자 프로필을 업데이트합니다.
        
        인자:
            conversation_history: 분석할 대화 기록
            
        반환값:
            업데이트된 프로필의 요약
        """
        await self.extract_profile_info(conversation_history)
        return self.get_profile_summary()
    
    def get_profile_summary(self) -> str:
        """
        현재 사용자 프로필의 요약을 가져옵니다.
        
        반환값:
            사용자 프로필을 요약한 문자열
        """
        return str(self.user_profile)
    
    def get_profile_as_dict(self) -> Dict[str, Any]:
        """
        사용자 프로필을 사전 형태로 가져옵니다.
        
        반환값:
            사전 형태의 사용자 프로필
        """
        return self.user_profile.to_dict()
    
    def get_missing_critical_info(self) -> List:
        """
        누락된 중요 정보 목록을 가져옵니다.
        
        반환값:
            누락된 중요 정보의 (필드, 표시명) 튜플 목록
        """
        return self.user_profile.get_missing_critical_info()
    
    def reset_profile(self) -> str:
        """
        사용자 프로필을 초기화합니다.
        
        반환값:
            확인 메시지
        """
        self.user_profile = InsuranceProfile()
        return "사용자 프로필이 초기화되었습니다."
    
    async def handle_message(
        self, 
        message: str, 
        chat_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        처리 전에 프로필을 업데이트하기 위해 handle_message 메소드를 재정의합니다.
        
        인자:
            message: 사용자 메시지
            chat_history: 대화 기록
            
        반환값:
            에이전트의 응답
        """
        # 먼저 대화 기록을 기반으로 프로필 업데이트
        await self.update_profile(chat_history)
        
        # 그 다음 일반적인 메시지 처리 진행
        return await super().handle_message(message, chat_history) 