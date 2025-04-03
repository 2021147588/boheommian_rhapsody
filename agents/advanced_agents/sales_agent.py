from agents.planner_agent.advanced_base_agent import AdvancedBaseAgent
import re
from openai import OpenAI
import os
import json

class InsuranceProfile:
    """
    한화손해보험 운전자보험 상담을 위한 고객 프로필 클래스
    대화 내용에서 추출한 정보를 업데이트하며 최적의 운전자보험 상담에 활용
    """
    def __init__(self):
        # 기본 인적사항 (핵심만 유지)
        self.name = None                  # 고객 이름
        self.age = None                   # 나이
        self.gender = None                # 성별
        self.occupation = None            # 직업
        
        # 운전 관련 정보
        self.driving_experience = None    # 운전 경력(년)
        self.vehicle_type = None          # 차량 종류(승용차/SUV/트럭 등)
        self.annual_mileage = None        # 연간 주행거리
        self.accident_history = []        # 사고 이력
        self.traffic_violations = []      # 교통법규 위반 이력
        self.commute_distance = None      # 출퇴근 거리
        self.main_driving_area = None     # 주 운전지역(도심/고속도로/시외 등)
        
        # 보험 관련 정보
        self.current_insurance = None     # 현재 자동차보험 가입 여부
        self.current_driver_insurance = None  # 현재 운전자보험 가입 여부
        self.budget_monthly = None        # 보험료 예산(월)
        self.coverage_preference = None   # 보장범위 선호(최소/일반/프리미엄)
        
        # 운전자보험 니즈
        self.priority_coverage = []       # 우선적으로 원하는 보장(교통사고처리지원금/벌금/변호사선임 등)
        self.pain_points = []             # 고객이 언급한 페인 포인트
        
        # 한화손해보험 관련 정보
        self.hanwha_customer_id = None    # 한화손해보험 고객 ID (기존 고객인 경우)
        self.inquiry_products = []        # 고객이 문의한 한화 운전자보험 상품
        self.preferred_contact_method = None  # 선호하는 연락 방식
        
    def update(self, extracted_info):
        """
        대화에서 추출한 정보로 프로필 업데이트
        
        Args:
            extracted_info (dict): 대화에서 추출한 고객 정보
        
        Returns:
            self: 업데이트된 프로필 객체
        """
        # 딕셔너리의 키가 있으면 해당 속성 업데이트
        for key, value in extracted_info.items():
            if hasattr(self, key) and value:
                if isinstance(getattr(self, key), list) and not isinstance(value, list):
                    # 리스트 속성에 단일 값 추가
                    getattr(self, key).append(value)
                else:
                    # 일반 속성 업데이트 또는 리스트 속성에 리스트 할당
                    setattr(self, key, value)
        
        return self
    
    def get_missing_critical_info(self):
        """
        운전자보험 상담을 위해 꼭 필요한 누락된 정보 목록 반환
        
        Returns:
            list: 누락된 중요 정보 필드 목록
        """
        critical_fields = {
            'age': '고객님의 연령대',
            'driving_experience': '운전 경력',
            'vehicle_type': '차량 종류',
            'commute_distance': '출퇴근 거리',
            'current_driver_insurance': '현재 운전자보험 가입 여부'
        }
        
        missing = []
        for field, display_name in critical_fields.items():
            if getattr(self, field) is None:
                missing.append((field, display_name))
                
        return missing
    
    def to_dict(self):
        """
        프로필을 딕셔너리 형태로 변환 (카테고리별로 구성)
        
        Returns:
            dict: 프로필 정보를 담은 딕셔너리
        """
        profile_dict = {}
        
        # 인적사항 섹션
        personal_info = {key: getattr(self, key) for key in 
                         ['name', 'age', 'gender', 'occupation']}
        profile_dict["인적사항"] = {k: v for k, v in personal_info.items() if v is not None}
        
        # 운전관련 정보 섹션
        driving_info = {key: getattr(self, key) for key in 
                       ['driving_experience', 'vehicle_type', 'annual_mileage', 
                        'accident_history', 'traffic_violations', 'commute_distance',
                        'main_driving_area']}
        profile_dict["운전정보"] = {k: v for k, v in driving_info.items() if v is not None}
        
        # 보험관련 정보 섹션
        insurance_info = {key: getattr(self, key) for key in 
                          ['current_insurance', 'current_driver_insurance', 
                           'budget_monthly', 'coverage_preference']}
        profile_dict["보험정보"] = {k: v for k, v in insurance_info.items() if v is not None}
        
        # 운전자보험 니즈 섹션
        needs_info = {key: getattr(self, key) for key in 
                      ['priority_coverage', 'pain_points']}
        profile_dict["운전자보험니즈"] = {k: v for k, v in needs_info.items() if v is not None}
        
        # 한화손해보험 관련 정보
        hanwha_info = {key: getattr(self, key) for key in 
                       ['hanwha_customer_id', 'inquiry_products', 'preferred_contact_method']}
        profile_dict["한화손해보험정보"] = {k: v for k, v in hanwha_info.items() if v is not None}
        
        return profile_dict
    
    def __str__(self):
        """
        프로필을 문자열로 표현
        
        Returns:
            str: 프로필 정보 문자열
        """
        profile_dict = self.to_dict()
        
        result = "====== 운전자보험 고객 프로필 ======\n"
        for section, items in profile_dict.items():
            if items:  # 섹션에 데이터가 있는 경우만 포함
                result += f"\n▶ {section}\n"
                for key, value in items.items():
                    result += f"  • {key}: {value}\n"
        
        # 중요 누락 정보 표시
        missing_info = self.get_missing_critical_info()
        if missing_info:
            result += "\n▶ 누락된 중요 정보\n"
            for field, display_name in missing_info:
                result += f"  • {display_name}\n"
        
        return result 

class AdvancedSalesAgent(AdvancedBaseAgent):
    def __init__(self):
        # 고객 프로필 초기화
        self.customer_profile = InsuranceProfile()
        
        super().__init__(
            name="Sales Agent",
            system_message=(
                "당신은 한화손해보험의 운전자보험 판매 전문가입니다. 다음 루틴에 따라 고객을 응대하세요:\n"
                "1. 고객과의 대화에서 프로필 정보를 자연스럽게 수집합니다. 특히 연령, 운전 경력, 차량 종류, 출퇴근 거리, 현재 보험 가입 여부에 집중하세요.\n"
                "2. 고객 정보가 충분히 수집되면 맞춤형 운전자보험 상품을 추천합니다.\n"
                "3. 다음 보장 내용을 중심으로 상품의 장점을 설명합니다: 교통사고처리지원금, 자동차사고변호사선임비용, 벌금, 면허정지/취소 위로금.\n"
                "4. 고객이 상세 정보를 요청하면 RAG 에이전트로 전환합니다.\n"
                "5. 고객이 구매에 관심을 보이면 상담 예약을 제안합니다.\n"
                "6. 대화 중 수집된 고객 정보를 지속적으로 프로필에 업데이트하고, 누락된 중요 정보가 있으면 자연스럽게 질문합니다.\n"
                "항상 친절하고 전문적으로 응대하며, 고객의 운전 상황과 필요에 맞는 최적의 보장 내용을 제안합니다."
            ),
            model="gpt-4o-mini",
            tools=[
                self.extract_and_update_profile,
                self.get_profile_summary,
                self.recommend_driver_insurance, 
                self.schedule_consultation, 
                self.transfer_to_rag_agent
            ]
        )
    
    def extract_profile_info(self, message: str):
        """
        LLM을 사용하여 사용자 메시지에서 프로필 정보를 추출합니다.
        
        Args:
            message (str): 사용자 메시지
            
        Returns:
            dict: 추출된 프로필 정보
        """
        from openai import OpenAI
        import os
        import json
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = f"""
        다음 대화에서 고객의 운전자보험 관련 정보를 추출해주세요. 
        정보가 없는 필드는 null로 남겨두고, 있는 정보만 채우세요.
        
        고객 메시지: {message}
        
        다음 JSON 형식으로 응답해주세요:
        {{
            "age": null 또는 숫자(나이),
            "gender": null 또는 문자열("남" 또는 "여"),
            "occupation": null 또는 문자열(직업),
            "driving_experience": null 또는 숫자(운전 경력, 년 단위. "없음"인 경우 0),
            "vehicle_type": null 또는 문자열(차량 종류),
            "annual_mileage": null 또는 숫자(연간 주행거리, km),
            "accident_history": [] 또는 문자열 배열(사고 이력),
            "traffic_violations": [] 또는 문자열 배열(교통법규 위반 이력),
            "commute_distance": null 또는 숫자(출퇴근 거리, km. "출퇴근 안함"인 경우 0),
            "main_driving_area": null 또는 문자열(주 운전지역),
            "current_insurance": null 또는 불리언(현재 자동차보험 가입 여부),
            "current_driver_insurance": null 또는 불리언(현재 운전자보험 가입 여부),
            "budget_monthly": null 또는 숫자(월 보험료 예산),
            "coverage_preference": null 또는 문자열(보장범위 선호),
            "priority_coverage": [] 또는 문자열 배열(우선적으로 원하는 보장),
            "pain_points": [] 또는 문자열 배열(고객이 언급한 페인 포인트),
            "preferred_contact_method": null 또는 문자열(선호하는 연락 방식)
        }}
        
        JSON 형식만 반환하고 다른 설명은 포함하지 마세요.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # 또는 사용 가능한 다른 모델
                messages=[{"role": "user", "content": prompt}],
                temperature=0,  # 결정적 응답을 위해 temperature를 0으로 설정
                response_format={"type": "json_object"}
            )
            
            # 응답에서 JSON 파싱
            extracted_info = json.loads(response.choices[0].message.content)
            
            # null 값 필터링 및 빈 리스트 확인
            filtered_info = {}
            for key, value in extracted_info.items():
                if value is not None and value != [] and value != "":
                    filtered_info[key] = value
            
            return filtered_info
            
        except Exception as e:
            print(f"Error extracting profile info: {e}")
            return {}
    
    def extract_and_update_profile(self, message: str):
        """
        사용자 메시지에서 LLM을 통해 정보를 추출하고 프로필을 업데이트합니다.
        
        Args:
            message (str): 사용자 메시지
        
        Returns:
            str: 업데이트 결과와 누락된 중요 정보 안내
        """
        # 메시지가 없거나 딕셔너리로 전달된 경우 처리
        if isinstance(message, dict) and 'message' in message:
            message = message['message']
        
        if not message or not isinstance(message, str):
            return "메시지 처리 중 오류가 발생했습니다."
        
        # LLM을 통해 정보 추출
        extracted_info = self.extract_profile_info(message)
        
        # 추출된 정보가 없는 경우
        if not extracted_info:
            return "메시지에서 프로필 정보를 추출할 수 없었습니다. 좀 더 자세한 정보를 제공해주세요."
        
        # 프로필 업데이트
        self.customer_profile.update(extracted_info)
        
        # 업데이트된 정보 필드명 한글화
        field_names = {
            'age': '나이', 
            'gender': '성별',
            'occupation': '직업',
            'vehicle_type': '차량 종류',
            'driving_experience': '운전 경력',
            'annual_mileage': '연간 주행거리',
            'accident_history': '사고 이력',
            'traffic_violations': '교통 위반 이력',
            'commute_distance': '출퇴근 거리',
            'main_driving_area': '주 운전지역',
            'current_insurance': '자동차보험 가입 여부',
            'current_driver_insurance': '운전자보험 가입 여부',
            'budget_monthly': '월 보험료 예산',
            'coverage_preference': '보장범위 선호',
            'priority_coverage': '우선 보장 항목',
            'pain_points': '우려사항',
            'preferred_contact_method': '선호 연락방식'
        }
        
        # 업데이트된 정보 목록 생성
        updated_fields = []
        for key in extracted_info:
            if key in field_names:
                value = extracted_info[key]
                if key == 'driving_experience' and value == 0:
                    updated_fields.append(f"{field_names[key]}: 없음")
                elif key == 'commute_distance' and value == 0:
                    updated_fields.append(f"{field_names[key]}: 출퇴근 안함")
                elif key in ['current_insurance', 'current_driver_insurance']:
                    updated_fields.append(f"{field_names[key]}: {'없음' if value is False else '있음'}")
                elif isinstance(value, list):
                    updated_fields.append(f"{field_names[key]}: {', '.join(value)}")
                else:
                    updated_fields.append(f"{field_names[key]}: {value}")
        
        if not updated_fields:
            return "새로운 프로필 정보가 추출되지 않았습니다."
        
        update_summary = ", ".join(updated_fields)
        
        # 누락된 중요 정보 확인
        missing_info = self.customer_profile.get_missing_critical_info()
        if missing_info:
            missing_fields = [display_name for _, display_name in missing_info]
            return f"다음 정보가 업데이트되었습니다: {update_summary}. 아직 {', '.join(missing_fields)}에 대한 정보가 필요합니다."
        else:
            return f"다음 정보가 업데이트되었습니다: {update_summary}. 이제 맞춤형 상품 추천이 가능합니다."
    
    def get_profile_summary(self):
        """
        현재 고객 프로필 요약을 반환합니다.
        
        Returns:
            str: 고객 프로필 요약
        """
        return str(self.customer_profile)
    
    def recommend_driver_insurance(self):
        """
        고객 프로필을 기반으로 운전자보험 상품을 추천합니다.
        
        Returns:
            str: 추천 상품 정보
        """
        profile = self.customer_profile
        missing_info = profile.get_missing_critical_info()
        
        if missing_info:
            missing_fields = [display_name for _, display_name in missing_info]
            return f"맞춤형 상품을 추천하기 위해 {', '.join(missing_fields)}에 대한 정보가 필요합니다."
        
        # 고객 특성에 따른 추천 상품 결정 로직
        products = []
        
        # 연령대별 추천
        age = profile.age
        if isinstance(age, int):
            if age < 30:
                products.append("한화 젊은 운전자보험")
            elif age < 50:
                products.append("한화 안심 운전자보험 플러스")
            else:
                products.append("한화 실버 운전자보험")
        
        # 운전 경력에 따른 추천
        experience = profile.driving_experience
        if isinstance(experience, int):
            if experience < 3:
                products.append("한화 초보 운전자 패키지")
        
        # 우선순위 보장 반영
        if profile.priority_coverage:
            if "교통사고처리지원금" in profile.priority_coverage:
                products.append("한화 교통사고처리지원 특화보험")
            if "벌금" in profile.priority_coverage:
                products.append("한화 법률비용지원 운전자보험")
        
        # 기본 추천 상품
        if not products:
            products.append("한화 통합 운전자보험")
        
        # 추천 이유 구성
        reasons = []
        if profile.age is not None:
            reasons.append(f"{profile.age}세 연령대")
        if profile.driving_experience is not None:
            reasons.append(f"운전 경력 {profile.driving_experience}년")
        if profile.vehicle_type is not None:
            reasons.append(f"{profile.vehicle_type} 운행")
        if profile.accident_history:
            reasons.append("사고 이력 고려")
        if profile.priority_coverage:
            reasons.append(f"{', '.join(profile.priority_coverage)} 보장 중시")
        
        # 기본 핵심 보장 내용
        core_coverages = [
            "교통사고처리지원금 (최대 2억원)",
            "자동차사고 변호사선임비용 (가입금액 한도)",
            "운전 중 사고벌금 (최대 2,000만원)",
            "면허정지/취소 위로금",
            "교통상해 입원일당"
        ]
        
        # 모든 정보 종합하여 추천 메시지 생성
        recommendation = (
            f"고객님의 운전 환경과 니즈를 분석한 결과, '{products[0]}' 상품을 추천드립니다.\n"
            f"추천 이유: {', '.join(reasons)}\n\n"
            f"핵심 보장 내용:\n"
        )
        
        for coverage in core_coverages:
            recommendation += f"• {coverage}\n"
            
        recommendation += "\n더 자세한 보장 내용이나 보험료 견적을 원하시면 말씀해주세요."
        
        return recommendation
    
    def schedule_consultation(self, name: str, phone: str, preferred_time: str):
        """
        운전자보험 상담 일정을 예약합니다.
        
        Args:
            name: 고객 이름
            phone: 연락처
            preferred_time: 선호 상담 시간
            
        Returns:
            str: 예약 확인 메시지
        """
        # 프로필에 이름과 연락처 정보 업데이트
        if name:
            self.customer_profile.name = name
        if phone:
            self.customer_profile.preferred_contact_method = f"전화 ({phone})"
            
        # 실제로는 CRM 시스템에 저장하는 로직이 필요합니다
        return (
            f"{name}님의 한화손해보험 운전자보험 상담이 {preferred_time}에 예약되었습니다. "
            f"전화번호 {phone}로 전문 상담사가 연락드릴 예정입니다. "
            f"상담 시 지금까지 파악된 고객님의 정보를 바탕으로 최적의 상품을 안내해 드리겠습니다."
        )
    
    def transfer_to_rag_agent(self):
        """
        고객이 상품에 대한 자세한 정보를 원할 때 RAG 에이전트로 전환합니다.
        """
        from agents.advanced_agents.rag_agent import AdvancedRAGAgent
        return AdvancedRAGAgent() 