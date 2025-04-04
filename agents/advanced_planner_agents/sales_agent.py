from agents.advanced_planner_agents.advanced_base_agent import AdvancedBaseAgent
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
        self.selected_product = None      # 고객이 선택한 상품
        
        # 고객 성향 분석 정보
        self.conversation_style = None    # 대화 스타일 (Open/Neutral/Reserved)
        self.decision_style = None        # 의사결정 스타일 (Rational/Neutral/Intuitive)
        self.persuasion_strategy = None   # 적용할 설득 전략 (Logical/Emotional/Social/Evidence)
        self.preferences = []             # 고객이 중요시하는 가치/선호사항
        
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
                       ['hanwha_customer_id', 'inquiry_products', 'preferred_contact_method', 'selected_product']}
        profile_dict["한화손해보험정보"] = {k: v for k, v in hanwha_info.items() if v is not None}
        
        # 고객 성향 정보
        personality_info = {key: getattr(self, key) for key in 
                       ['conversation_style', 'decision_style', 'persuasion_strategy', 'preferences']}
        profile_dict["고객성향정보"] = {k: v for k, v in personality_info.items() if v is not None}
        
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
        
        # OpenAI 클라이언트 초기화
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # 초기 메시지 (추천 에이전트에서 설정할 수 있음)
        self.initial_message = None
        
        # 한화 운전자보험 상품 정보
        self.insurance_products = """
            "자동차사고변호사선임비용Ⅴ": {"고급형": "5,000만원", "표준형": "5,000만원", "3400형": "5,000만원", "description": "자동차 운전 중 사고로 타인 상해 발생 시 구속, 공소 제기, 정식재판 청구, 경찰조사 후 불송치/약식기소/불기소 시 변호사 선임 비용 실손 보상 (공탁금 70% 선지급 가능)"},
            "자동차사고대인벌금Ⅱ": {"고급형": "3,000만원", "표준형": "3,000만원", "3400형": "3,000만원", "description": "자동차 운전 중 또는 비탑승 중 사고로 타인 신체 상해 관련 벌금 확정 시 실손 보상 (일반 2천만원 한도, 스쿨존 어린이 치사상 시 3천만원 한도)"},
            "자동차사고대물벌금": {"고급형": "500만원", "표준형": "500만원", "3400형": "500만원", "description": "자동차 운전 중 사고로 도로교통법 제151조에 따른 대물 벌금형 확정 시 실손 보상 (음주/무면허 제외)"},
            "대인형사합의실손비Ⅲ": {"고급형": "2억원", "표준형": "2억원", "3400형": "2억원", "description": "자동차 운전 중 또는 비탑승 중 사고로 타인 사망, 중상해(공소제기 또는 부상등급 1~3급), 중대법규위반(42일 이상 진단, 스쿨존 42일 미만 포함) 시 형사합의금 실손 보상 (공탁금 100% 선지급 가능)"},
            "원격지사고시운반비용": {"고급형": "20만원", "표준형": "20만원", "3400형": "20만원", "description": "자가용 운전 중 원격지(20km 초과 이동) 사고 시 발생한 운반 비용 실손 보상 (1사고당 한도)"},
            "보복운전피해보장": {"고급형": "10만원", "표준형": "50만원", "3400형": "50만원", "description": "보복운전 피해자로 공소제기 또는 기소유예 시 보험가입금액 지급 (1사고당 1회)"},
            "보복운전피해보장Ⅱ": {"고급형": "50만원", "표준형": "50만원", "3400형": "50만원", "description": "보복운전 피해로 신체 피해 또는 자동차/부착물 손해 발생 및 공소제기/기소유예 시 보험가입금액 지급 (정신적/심리적 피해만 있는 경우 제외, 1사고당 1회)"},
            "대인형사합의실손비Ⅲ (중대법규위반, 42일미만)": {"고급형": "1,000만원", "표준형": "1,000만원", "3400형": "1,000만원", "description": "자동차 운전 중 중대법규위반 사고로 타인에게 42일 미만 진단 발생 시 형사합의금 실손 보상 (진단일수별 차등, 공탁금 100% 선지급 가능)"},
            "자동차사고부상발생금 (1-7급, 단일지급)": {"고급형": "-", "표준형": "100만원", "3400형": "500만원", "description": "자동차사고로 부상등급 1~7급 해당 시 보험가입금액 지급"},
            "자동차사고부상발생금 (1-14급, 차등지급)": {"고급형": "-", "표준형": "10만원", "3400형": "30만원", "description": "자동차사고로 부상등급 1~14급 해당 시 부상등급별 차등 지급 (보험가입금액 기준)"},
            "교통상해사망": {"고급형": "-", "표준형": "1,000만원", "3400형": "5,000만원", "description": "교통상해사고로 사망 시 보험가입금액 지급"},
            "상해수술비": {"고급형": "-", "표준형": "10만원", "3400형": "50만원", "description": "상해사고의 직접 결과로 수술 시 보험가입금액 지급 (1회 한)"},
            "상해흉터복원수술비Ⅱ": {"고급형": "-", "표준형": "1,000만원", "3400형": "1,000만원", "description": "상해 치료 후 안면부/상지/하지 흉터 발생 시 원상회복 목적의 성형수술 비용 (사고 후 2년 내, 1cm당 차등 지급, 동일부위 1회 한)"},
            "응급실내원치료비 (응급)": {"고급형": "-", "표준형": "1만원", "3400형": "3만원", "description": "상해 또는 질병으로 응급환자에 해당하여 응급실 내원 진료 시 (1회당)"},
            "응급실내원치료비 (비응급)": {"고급형": "-", "표준형": "1만원", "3400형": "3만원", "description": "비응급환자이나 상해 또는 질병으로 응급실 내원 진료 시 (1회당)"},
            "골절 (치아파절제외) 진단비": {"고급형": "-", "표준형": "10만원", "3400형": "30만원", "description": "상해사고로 골절(치아파절 제외) 진단 확정 시 (1회 한)"},
            "깁스치료비": {"고급형": "-", "표준형": "10만원", "3400형": "30만원", "description": "질병 또는 상해로 깁스(Cast) 치료 시 (부목 제외, 1회 한)"},
            "골절 (치아파절제외) 깁스치료비": {"고급형": "-", "표준형": "-", "3400형": "20만원", "description": "골절(치아파절 제외) 진단 후 깁스(Cast) 치료 시 (1회 한)"},
            "골절 (치아파절제외) 부목치료비": {"고급형": "-", "표준형": "-", "3400형": "5만원", "description": "골절(치아파절 제외) 진단 후 부목(Splint Cast) 치료 시 (1회 한)"},
            "특정상해성뇌손상진단비": {"고급형": "-", "표준형": "-", "3400형": "100만원", "description": "특정상해성뇌손상 진단 확정 시 (최초 1회)"},
            "특정상해성장기손상진단비": {"고급형": "-", "표준형": "-", "3400형": "100만원", "description": "특정상해성장기손상 진단 확정 시 (최초 1회)"},
            "특정상해성뇌출혈진단비": {"고급형": "-", "표준형": "-", "3400형": "1,000만원", "description": "특정상해성뇌출혈 진단 확정 시 (최초 1회)"},
            "상해성뇌출혈수술비": {"고급형": "-", "표준형": "-", "3400형": "100만원", "description": "상해성뇌출혈 진단 후 직접 치료 목적 수술 시 (수술 1회당)"},
            "민사소송법률비용Ⅱ (실손)": {"고급형": "-", "표준형": "-", "3400형": "3,000만원", "description": "보험기간 중 민사소송 제기되어 판결/조정/화해로 종료 시 법률비용 실손 보상 (변호사비용 2천만원, 인지/송달료 1천만원 한도, 자기부담금 있음)"}
        """
        
        super().__init__(
            name="Sales Agent",
            system_message=(
                "당신은 한화손해보험의 운전자보험 판매 전문가입니다. 다음 루틴에 따라 고객을 응대하세요:\n"
                "1. 고객과의 대화에서 프로필 정보를 자연스럽게 수집합니다. 특히 연령, 운전 경력, 차량 종류, 출퇴근 거리, 현재 보험 가입 여부에 집중하세요.\n"
                "2. 고객의 성향(의사결정 스타일, 대화 스타일)을 대화를 통해 파악하고 그에 맞는 맞춤형 설득 전략을 사용합니다.\n"
                "3. 구체적인 상품 추천이 필요하면 추천 에이전트로 연결하여 맞춤형 상품을 추천받도록 안내합니다.\n"
                "4. 고객이 선택한 상품에 대해 적절한 설득 전략을 사용하여 구매 결정을 돕습니다.\n"
                "5. 가입 과정, 필요 서류, 보장 시작일 등 실무적인 내용을 명확하게 설명합니다.\n"
                "6. 상세 정보를 요청받으면 RAG 에이전트로 전환합니다.\n"
                "항상 친절하고 전문적으로 응대하며, 고객의 성향에 맞는 설득 방식을 적용하되 지나친 판매 압박은 하지 않습니다."
                
                "\n\n중요: 당신의 최종 목표는 고객이 보험에 가입하도록 설득하는 것입니다. 고객이 추천 상품에 의문을 표하거나 '왜 이 보험이 내게 좋은지' 물어볼 때 다음 설득 전략을 활용하세요:"
                
                "\n\n[설득 전략]"
                "\n1. 개인 맞춤형 제안 전략: 고객의 운전 경력, 차종, 생활 패턴 등 구체적인 정보를 바탕으로 '이 보험이 고객님에게 특별히 맞는 이유'를 명확히 설명하세요."
                "\n2. 리스크 대비 보장 강조 전략: 교통사고 시 예상되는 경제적 손실과 법적 책임을 구체적으로 설명하고, 추천 상품이 이러한 위험을 어떻게 커버하는지 강조하세요."
                "\n3. 스토리텔링 활용 전략: 비슷한 상황의 다른 고객이 보험을 통해 위기를 극복한 실제 사례를 공유하여 공감을 이끌어내세요."
                "\n4. 긴급성 및 한정 제안 전략: 현재 이용 가능한 특별 프로모션이나 할인 혜택을 강조하여 즉각적인 결정을 유도하세요."
                "\n5. 상호 신뢰 구축 전략: 고객의 우려사항을 경청하고 투명하게 답변하여 신뢰를 구축하세요."
                
                "\n\n대화 목표:"
                "\n1. 고객과 자연스러운 대화를 통해 필요한 정보를 수집하세요"
                "\n2. 고객의 상황과 니즈에 맞는 한화 운전자보험 상품을 추천하세요"
                "\n3. 고객이 망설이거나 질문하면 적절한 설득 전략을 사용하세요"
                "\n4. 고객이 보험 가입에 동의하도록 유도하세요 (이것이 최종 목표입니다)"
                
                "\n\n주요 태스크:"
                "\n- 고객 정보를 기반으로 최적의 보험 상품을 추천하세요"
                "\n- 고객이 '왜 이 보험이 자신에게 맞는지' 물어보면 개인화된 이유를 반드시 제시하세요"
                "\n- 언제나 친절하고 전문적인 태도를 유지하세요"
                
                "\n\n고객이 '이 상품이 왜 나에게 좋은가요?'라고 물으면 반드시 고객의 개인 정보와 상황에 맞춰 구체적인 이유를 제시하세요. 일반적인 답변이 아닌 맞춤형 설명이 가입 결정에 핵심입니다."
                
                "\n\n고객이 가입 의사를 표현하면(예: '가입하겠습니다', '신청할게요') 즉시 축하하고 다음 단계를 안내하세요. 이것이 성공적인 상담의 목표입니다."
            ),
            model="gpt-4o-mini",
            tools=[
                self.extract_and_update_profile,
                self.get_profile_summary,
                self.analyze_customer_personality,
                self.apply_persuasion_strategy,
                self.set_selected_product,
                self.process_purchase_interest,
                self.explain_purchase_process,
                self.schedule_consultation,
                self.transfer_to_recommendation_agent,
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
            "preferred_contact_method": null 또는 문자열(선호하는 연락 방식),
            "selected_product": null 또는 문자열(고객이 언급한 특정 상품명),
            "inquiry_products": [] 또는 문자열 배열(고객이 문의한 상품명),
            "preferences": [] 또는 문자열 배열(고객이 중요시하는 가치/선호사항)
        }}
        
        JSON 형식만 반환하고 다른 설명은 포함하지 마세요.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
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
            'preferred_contact_method': '선호 연락방식',
            'selected_product': '선택한 상품',
            'inquiry_products': '문의한 상품'
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
            return f"다음 정보가 업데이트되었습니다: {update_summary}."
    
    def get_profile_summary(self):
        """
        현재 고객 프로필 요약을 반환합니다.
        
        Returns:
            str: 고객 프로필 요약
        """
        return str(self.customer_profile)
    
    def set_selected_product(self, product_name: str):
        """
        고객이 선택한 상품을 프로필에 설정합니다.
        
        Args:
            product_name: 상품명
        
        Returns:
            str: 처리 결과 메시지
        """
        self.customer_profile.selected_product = product_name
        return f"'{product_name}'을(를) 고객님의 선택 상품으로 설정했습니다."
    
    def process_purchase_interest(self):
        """
        고객의 구매 의향을 처리하고 다음 단계를 안내합니다.
        
        Returns:
            str: 구매 절차 안내 메시지
        """
        profile = self.customer_profile
        selected_product = profile.selected_product
        
        if not selected_product:
            return "구매를 진행하기 전에 선택하신 상품이 필요합니다. 관심 있는 상품을 알려주시겠어요?"
        
        # 가입 절차 설명 프롬프트 구성
        prompt = f"""
        다음 고객 정보를 바탕으로, '{selected_product}' 가입을 위한 다음 단계와 필요 서류를 안내해주세요:
        
        고객 정보:
        {json.dumps(profile.to_dict(), ensure_ascii=False, indent=2)}
        
        다음 내용을 포함해주세요:
        1. 필요한 서류 목록
        2. 가입 방법 (온라인/전화/대면 상담)
        3. 소요 예상 시간
        4. 보험 효력 발생 시점
        
        고객 친화적이고 명확한 설명으로 작성해주세요.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error processing purchase interest: {e}")
            return f"'{selected_product}' 상품 가입을 위해 신분증과 보험 청약서가 필요합니다. 자세한 안내를 원하시면 상담 예약을 도와드리겠습니다."
    
    def explain_purchase_process(self, product_name: str = None):
        """
        보험 가입 과정을 상세히 설명합니다.
        
        Args:
            product_name: 상품명 (지정되지 않은 경우 선택된 상품 사용)
            
        Returns:
            str: 가입 절차 설명
        """
        if not product_name:
            product_name = self.customer_profile.selected_product
            
        if not product_name:
            return "가입 절차를 설명하기 위해 어떤 상품에 관심이 있으신지 알려주세요."
        
        prompt = f"""
        '{product_name}' 운전자보험 가입 절차에 대해 상세히 설명해주세요.
        
        다음 내용을 포함해주세요:
        1. 가입 전 준비사항
        2. 청약 절차
        3. 필요 서류
        4. 심사 과정
        5. 보험 개시일 결정 방식
        6. 보험증권 수령 방법
        7. 첫 보험료 납부 방법과 시기
        
        고객이 이해하기 쉽게 단계별로 설명해주세요.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error explaining purchase process: {e}")
            return f"""
{product_name} 가입 절차는 다음과 같습니다:

1. 청약서 작성: 개인정보와 원하는 보장 내용을 확인하고 서명합니다.
2. 초회보험료 납입: 첫 달 보험료를 납부합니다.
3. 심사 과정: 보험사에서 가입 심사를 진행합니다 (보통 1-2일 소요).
4. 보험증권 발급: 승인 후 보험증권이 발급됩니다.
5. 보장 개시: 청약일로부터 보통 다음 날부터 보장이 시작됩니다.

필요 서류는 신분증, 자동차등록증(해당 시), 운전면허증입니다.
더 자세한 안내를 원하시면 1:1 상담을 예약해 드리겠습니다.
"""
    
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
        product_info = ""
        if self.customer_profile.selected_product:
            product_info = f" {self.customer_profile.selected_product} 상품에 관한"
            
        return (
            f"{name}님의 한화손해보험 운전자보험{product_info} 상담이 {preferred_time}에 예약되었습니다. "
            f"전화번호 {phone}로 전문 상담사가 연락드릴 예정입니다. "
            f"상담 시 지금까지 파악된 고객님의 정보를 바탕으로 최적의 상품을 안내해 드리겠습니다."
        )
    
    def transfer_to_recommendation_agent(self):
        """
        상품 추천이 필요할 때 추천 에이전트로 전환합니다.
        """
        from agents.advanced_planner_agents.recommendation_agent import AdvancedRecommendationAgent
        return AdvancedRecommendationAgent()
    
    def transfer_to_rag_agent(self):
        """
        고객이 상품에 대한 자세한 정보를 원할 때 RAG 에이전트로 전환합니다.
        """
        from agents.advanced_planner_agents.rag_agent import AdvancedRAGAgent
        return AdvancedRAGAgent()
    
    def analyze_customer_personality(self, conversation_history: str):
        """
        고객과의 대화 내용을 분석하여 성향을 파악합니다.
        
        Args:
            conversation_history: 대화 이력
            
        Returns:
            str: 성향 분석 결과
        """
        prompt = f"""
        다음 대화 내용을 바탕으로 고객의 성향을 분석해주세요. 직접적으로 고객에게 성향을 묻지 않고, 
        대화에서 드러나는 특성을 바탕으로 추론해야 합니다.

        대화 내용:
        {conversation_history}

        다음 JSON 형식으로 응답해주세요:
        {{
            "conversation_style": "Open" 또는 "Neutral" 또는 "Reserved" (대화에 얼마나 개방적인지),
            "decision_style": "Rational" 또는 "Neutral" 또는 "Intuitive" (의사결정 방식),
            "persuasion_strategy": "Logical" 또는 "Emotional" 또는 "Social" 또는 "Evidence" (가장 효과적일 설득 전략),
            "preferences": [] (고객이 중요시하는 가치/선호사항 문자열 배열),
            "analysis_summary": "분석 요약 (100자 이내)"
        }}
        
        JSON 형식만 반환하고 다른 설명은 포함하지 마세요.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            # 응답에서 JSON 파싱
            personality_analysis = json.loads(response.choices[0].message.content)
            
            # 프로필 업데이트
            self.customer_profile.conversation_style = personality_analysis.get("conversation_style")
            self.customer_profile.decision_style = personality_analysis.get("decision_style")
            self.customer_profile.persuasion_strategy = personality_analysis.get("persuasion_strategy")
            
            if personality_analysis.get("preferences"):
                self.customer_profile.preferences = personality_analysis.get("preferences")
            
            return f"""
고객 성향 분석 결과:
- 대화 스타일: {personality_analysis.get("conversation_style")}
- 의사결정 스타일: {personality_analysis.get("decision_style")}
- 효과적인 설득 전략: {personality_analysis.get("persuasion_strategy")}
- 주요 선호사항: {', '.join(personality_analysis.get("preferences", []))}

{personality_analysis.get("analysis_summary", "")}
"""
            
        except Exception as e:
            print(f"Error analyzing personality: {e}")
            return "고객 성향 분석 중 오류가 발생했습니다."
    
    def apply_persuasion_strategy(self, product_id: str = None):
        """
        고객 성향에 맞는 설득 전략을 적용하여 추천 상품을 안내합니다.
        
        Args:
            product_id: 상품 ID (미지정 시 선택된 상품 사용)
            
        Returns:
            str: 맞춤형 설득 메시지
        """
        if not product_id:
            product_id = self.customer_profile.selected_product
            
        if not product_id:
            return "설득 전략을 적용할 상품이 선택되지 않았습니다. 먼저 상품을 선택해주세요."
        
        # 고객 성향 확인
        if not self.customer_profile.persuasion_strategy:
            # 성향 분석이 없을 경우 기본값 설정
            self.customer_profile.persuasion_strategy = "Logical"
            
        # 상품 정보 가져오기
        try:
            # 상품 기본 정보
            product_types = {
                "차도리운전자보험": "고급형",
                "차도리운전자보험Plus": "표준형",
                "차도리ECO운전자보험": "표준형",
                "차도리운전자보험VIP": "3400형"
            }
            
            product_descriptions = {
                "차도리운전자보험": {
                    "advantages": ["합리적인 보험료", "기본적인 보장 제공", "가입 과정 간소화"],
                    "target": "모든 연령대, 처음 가입하는 고객"
                },
                "차도리운전자보험Plus": {
                    "advantages": ["확장된 보장 범위", "교통상해입원일당 포함", "면허취소위로금 지원"],
                    "target": "안전에 높은 가치를 두는 고객, 장기 운전자"
                },
                "차도리ECO운전자보험": {
                    "advantages": ["친환경차 특화 보장", "충전 중 상해 보장", "배터리 교체비용 지원"],
                    "target": "친환경차 운전자, 환경을 생각하는 가치 중시"
                },
                "차도리운전자보험VIP": {
                    "advantages": ["최고 수준의 보장", "교통상해사망 보장", "자동차사고성형수술비 지원"],
                    "target": "완벽한 보장을 원하는 고객, 안전과 보장에 높은 가치를 둠"
                }
            }
            
            # 선택한 상품의 정보
            product_type = product_types.get(product_id, "표준형")  # 기본값 "표준형"
            product_desc = product_descriptions.get(product_id, {
                "advantages": ["맞춤형 보장", "한화손해보험의 신뢰성", "전문 상담사의 관리"],
                "target": "모든 고객"
            })
            
            product = {
                "name": product_id,
                "advantages": product_desc["advantages"],
                "target": product_desc["target"],
                "type": product_type
            }
            
            # 보장 내용 정보 추출
            coverage_details = []
            try:
                # self.insurance_products에서 해당 상품 유형의 보장 내용 추출
                insurance_dict = json.loads("{" + self.insurance_products + "}")
                
                for coverage_name, coverage_info in insurance_dict.items():
                    if coverage_info.get(product_type) and coverage_info.get(product_type) != "-":
                        coverage_details.append({
                            "name": coverage_name,
                            "amount": coverage_info.get(product_type),
                            "description": coverage_info.get("description", "")
                        })
            except Exception as e:
                print(f"Error parsing insurance products: {e}")
                # 기본 보장 내용 설정
                coverage_details = [
                    {"name": "자동차사고변호사선임비용", "amount": "5,000만원", "description": "자동차 운전 중 사고로 변호사 선임 비용 보장"},
                    {"name": "자동차사고대인벌금", "amount": "3,000만원", "description": "자동차 운전 중 사고로 발생한 대인 벌금 보장"},
                    {"name": "대인형사합의실손비", "amount": "2억원", "description": "자동차 운전 중 사고로 발생한 형사합의금 보장"}
                ]
            
            # 고객 프로필 요약
            profile_summary = json.dumps(self.customer_profile.to_dict(), ensure_ascii=False)
            
            # 설득 전략별 프롬프트 구성
            strategy_prompt = {
                "Logical": f"고객이 합리적인 의사결정을 중요시합니다. {product['name']} 상품의 객관적인 장점, 비용 대비 효율성, 고객 상황에 맞는 합리적인 이유를 중심으로 설득 메시지를 작성해주세요.",
                "Emotional": f"고객은 감정적인 의사결정을 하는 경향이 있습니다. {product['name']} 상품이 제공하는 안정감, 안전, 가족 보호 등의 감성적 가치를 중심으로 설득 메시지를 작성해주세요.",
                "Social": f"고객은 사회적 증거와 타인의 의견을 중요시합니다. {product['name']} 상품을 많은 사람들이 선택한 이유, 만족도, 신뢰성 등 사회적 증거를 중심으로 설득 메시지를 작성해주세요.",
                "Evidence": f"고객은 구체적인 증거와 데이터를 중요시합니다. {product['name']} 상품의 구체적인 보장 내용, 수치, 통계, 사례 등 증거 기반 정보를 중심으로 설득 메시지를 작성해주세요."
            }
            
            # 고객 성향에 맞는 프롬프트 선택
            persuasion_prompt = strategy_prompt.get(
                self.customer_profile.persuasion_strategy, 
                strategy_prompt["Logical"]
            )
            
            # 주요 보장 내용 문자열 구성
            coverage_text = ""
            for coverage in coverage_details[:5]:  # 주요 보장 5개만 포함
                coverage_text += f"- {coverage['name']}: {coverage['amount']} ({coverage['description']})\n"
            
            # 최종 프롬프트 구성
            prompt = f"""
            다음 고객 정보와 상품 정보를 바탕으로 맞춤형 설득 메시지를 작성해주세요.
            
            고객 정보:
            {profile_summary}
            
            상품 정보:
            - 이름: {product['name']}
            - 주요 장점: {', '.join(product['advantages'])}
            - 주요 타겟: {product['target']}
            - 상품 유형: {product_type}
            
            주요 보장 내용:
            {coverage_text}
            
            설득 전략:
            {persuasion_prompt}
            
            아래의 설득 전략을 모두 활용하여 강력한 설득 메시지를 작성하세요:
            
            1. 개인 맞춤형 제안 전략: 고객의 운전 경력, 차종, 생활 패턴 등을 활용하여 "특별히 고객님께 맞는 이유"를 구체적으로 설명
            2. 리스크 대비 보장 강조 전략: 교통사고 시 발생할 경제적/법적 위험을 설명하고 이 상품이 어떻게 보호하는지 강조
            3. 스토리텔링 활용 전략: 비슷한 상황의 고객이 보험을 통해 혜택을 받은 사례 공유
            4. 긴급성 및 한정 제안 전략: 지금 가입 시 받을 수 있는 특별 혜택이나 프로모션 강조
            5. 상호 신뢰 구축 전략: 고객의 우려사항을 해소하고 투명한 정보 제공
            
            고객을 설득하여 가입하도록 하는 것이 핵심 목표임을 기억하세요. 고객의 질문이나 우려에 대해 명확하고 개인화된 답변을 제공하되, 궁극적으로는 가입 결정을 유도해야 합니다.
            
            최종 메시지는 비즈니스적이지만 친근하고, 전문적이면서도 공감을 이끌어내는 톤으로 작성하세요.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error applying persuasion strategy: {e}")
            return f"{product_id} 상품은 고객님의 상황에 가장 적합한 선택입니다. 자세한 안내를 원하시면 상담을 예약해 드리겠습니다." 