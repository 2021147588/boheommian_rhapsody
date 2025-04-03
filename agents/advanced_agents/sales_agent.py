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
        
        # 사용자가 제공한 설득 전략
        persuasion_strategies = """
        [설득 전략]
        1. 개인 맞춤형 제안 전략: 고객의 생활 패턴, 가족 구성, 재무 상황 등 구체적인 정보를 바탕으로 개인에게 가장 적합한 보험 상품을 제안합니다.
        2. 리스크 대비 보장 강조 전략: 예상치 못한 위험이나 사고 발생 시, 발생할 수 있는 경제적 부담과 감정적 충격을 강조하여 보험의 필요성을 부각시킵니다.
        3. 스토리텔링 활용 전략: 실제 사례나 성공 사례, 또는 고객의 공감을 이끌어낼 수 있는 이야기를 통해 보험의 가치를 전달합니다.
        4. 긴급성 및 한정 제안 전략: 현재의 특혜나 한정된 혜택, 프로모션 등을 강조하여 고객이 빠른 결정을 내리도록 유도합니다.
        5. 상호 신뢰 구축 전략: 고객과의 신뢰를 바탕으로 장기적인 관계 형성을 목표로 하며, 투명하고 친절한 상담을 통해 고객의 의문점과 불안을 해소합니다.
        """

        # 보험 상품 정보 (실제 상품 정보 로딩 로직 필요)
        # 예시: 실제로는 RecommendationAgent의 DB 등에서 가져와야 함
        # insurance_products = "사용 가능한 한화손해보험 운전자 보험 상품 목록:\n- 고급형\n- 표준형\n- 3400형"
        # 여기서는 Recommendation Agent의 DB를 직접 참조하기 어려우므로,
        # 필요시 Recommendation Agent를 통해 상품 정보를 얻어오거나 별도로 관리해야 합니다.
        # 임시로 플레이스홀더 또는 간단한 설명을 넣습니다.
        insurance_products_info = """
        [주요 보험 플랜]
        - 고급형: 포괄적인 보장을 원하는 고객에게 적합
        - 표준형: 균형 잡힌 보장을 원하는 고객에게 적합
        - 3400형: 필수적인 핵심 보장을 원하는 고객에게 적합
        (상세 내용은 추천 에이전트 또는 RAG 에이전트를 통해 확인 가능)
        """

        # 새로운 시스템 프롬프트 구성
        new_system_message = f"""
        당신은 한화손해보험의 운전자보험 판매 전문가입니다.
        고객의 정보를 바탕으로 최적의 보험 상품(플랜 유형)을 추천하고, 고객이 보험에 가입하도록 설득하는 것이 궁극적인 목표입니다.

        ## 대화 목표
        1. 고객과 자연스러운 대화를 통해 필요한 정보(연령, 운전 경력, 차량 종류, 예산 등)를 수집하세요.
        2. 고객이 망설이거나 질문하면, 아래 제공된 설득 전략 중 가장 적절한 것을 선택하여 추천한 보험의 가치를 설명하고 고객의 우려를 해소하세요.
        3. 고객이 보험 가입에 긍정적인 반응을 보이도록 유도하고, 최종적으로 가입 의사를 명확히 표현하도록 이끄세요. (이것이 최종 목표입니다)

        ## 주요 태스크
        - 고객 정보를 지속적으로 수집하고 `InsuranceProfile`을 업데이트하세요 (`extract_and_update_profile` 도구 사용).
        - 고객에게 보험 플랜 유형을 추천할 때는 반드시 '왜 이 플랜이 고객님께 맞는지' 개인화된 이유를 제시하세요. (고객 프로필 정보 활용)
        - 고객이 비협조적이거나, 망설이거나, 반론을 제기할 경우, 아래 설득 전략을 상황에 맞게 창의적으로 적용하여 응대하세요.
        - 상품의 세부적인 약관이나 보장 내용에 대한 깊은 질문은 RAG 에이전트에게 넘기세요. (`transfer_to_rag_agent` 도구 사용)
        - 복잡한 상품 비교나 개인 맞춤 추천이 필요하면 추천 에이전트에게 넘기세요. (`transfer_to_recommendation_agent` 도구 사용)
        - 항상 친절하고 전문적인 태도를 유지하며, 고객과의 신뢰를 구축하세요.

        {persuasion_strategies}

        {insurance_products_info}

        **중요**: 당신의 임무는 단순히 정보를 제공하는 것이 아니라, 고객이 **"가입하겠습니다", "가입할게요", "신청합니다"** 와 같이 명확한 가입 의사를 표현하도록 적극적으로 설득하는 것입니다. 대화의 마지막은 고객의 가입 결정으로 마무리되어야 합니다.
        """

        super().__init__(
            name="Sales Agent",
            system_message=new_system_message, # 수정된 시스템 메시지 적용
            model="gpt-4o-mini",
            tools=[
                self.extract_and_update_profile,
                self.get_profile_summary,
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
        (이 메서드는 크게 변경할 필요 없음, 필요시 JSON 필드 조정)
        """
        prompt = f"""
        다음 대화에서 고객의 운전자보험 관련 정보를 추출해주세요.
        정보가 없는 필드는 null로 남겨두고, 있는 정보만 채우세요.

        고객 메시지: {message}

        다음 JSON 형식으로 응답해주세요 (주요 필드 위주):
        {{
            "name": null 또는 문자열(고객 이름),
            "age": null 또는 숫자(나이),
            "gender": null 또는 문자열("남" 또는 "여"),
            "occupation": null 또는 문자열(직업),
            "driving_experience": null 또는 숫자(운전 경력, 년 단위. "없음"인 경우 0),
            "vehicle_type": null 또는 문자열(차량 종류),
            "commute_distance": null 또는 숫자(출퇴근 거리, km. "출퇴근 안함"인 경우 0),
            "current_driver_insurance": null 또는 불리언(현재 운전자보험 가입 여부),
            "budget_monthly": null 또는 숫자(월 보험료 예산),
            "coverage_preference": null 또는 문자열(선호 보장 수준),
            "priority_coverage": [] 또는 문자열 배열(우선 보장 항목),
            "pain_points": [] 또는 문자열 배열(우려사항),
            "preferred_contact_method": null 또는 문자열(선호 연락 방식),
            "selected_plan_type": null 또는 문자열(고객이 선택/언급한 플랜 유형: "고급형", "표준형", "3400형"),
            "inquiry_products": [] 또는 문자열 배열(고객이 문의한 상품/플랜 유형),
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
            extracted_info = json.loads(response.choices[0].message.content)
            # null 값 및 빈 리스트 필터링
            return {k: v for k, v in extracted_info.items() if v is not None and v != [] and v != ""}
        except Exception as e:
            print(f"Error extracting profile info: {e}")
            return {}
    
    def extract_and_update_profile(self, message: str):
        """
        사용자 메시지에서 LLM을 통해 정보를 추출하고 프로필을 업데이트합니다.
        (프로필 필드명에 맞춰 한글화 부분 등 업데이트 필요 시 조정)
        """
        if isinstance(message, dict) and 'message' in message:
            message = message['message']

        if not message or not isinstance(message, str):
            # LLM에게 처리 요청 메시지 반환 (정보 부족 시 질문 유도)
            return "고객님의 상황에 대해 조금 더 자세히 말씀해주시겠어요? 예를 들어, 운전 경력이나 주로 운전하시는 차량 종류 등이 궁금합니다."

        extracted_info = self.extract_profile_info(message)

        if not extracted_info:
             # LLM에게 처리 요청 메시지 반환 (정보 부족 시 질문 유도)
            return "말씀 감사합니다. 혹시 운전자 보험 관련해서 더 궁금하신 점이나 중요하게 생각하시는 부분이 있으신가요?"

        self.customer_profile.update(extracted_info)

        # 필드 이름 매핑 (InsuranceProfile의 속성과 일치하도록)
        field_names = {
            'name': '고객명', 'age': '나이', 'gender': '성별', 'occupation': '직업',
            'driving_experience': '운전 경력', 'vehicle_type': '차량 종류',
            'annual_mileage': '연간 주행거리', 'accident_history': '사고 이력',
            'traffic_violations': '교통 위반 이력', 'commute_distance': '출퇴근 거리',
            'main_driving_area': '주 운전지역', 'current_insurance': '자동차보험 가입 여부',
            'current_driver_insurance': '운전자보험 가입 여부', 'budget_monthly': '월 보험료 예산',
            'coverage_preference': '선호 보장 수준', 'priority_coverage': '우선 보장 항목',
            'pain_points': '우려사항', 'preferred_contact_method': '선호 연락방식',
            'selected_plan_type': '선택 플랜 유형', # selected_product 대신 plan_type 사용
            'inquiry_products': '문의 상품/플랜', 'preferences': '주요 선호사항'
        }

        updated_fields = []
        for key, value in extracted_info.items():
             if key in field_names:
                 # 값 포맷팅
                 formatted_value = value
                 if key == 'driving_experience' and value == 0: formatted_value = "없음"
                 elif key == 'commute_distance' and value == 0: formatted_value = "출퇴근 안함"
                 elif key in ['current_insurance', 'current_driver_insurance']: formatted_value = '있음' if value else '없음'
                 elif isinstance(value, list): formatted_value = ', '.join(map(str, value))
                 else: formatted_value = str(value)

                 updated_fields.append(f"{field_names[key]}: {formatted_value}")

        if not updated_fields:
            # LLM이 다음 질문을 하도록 유도
             return "네, 알겠습니다. 더 필요하신 정보나 궁금한 점이 있으시면 언제든지 말씀해주세요."

        update_summary = ", ".join(updated_fields)

        # 중요 정보 누락 시 다음 질문 유도
        missing_info = self.customer_profile.get_missing_critical_info()
        if missing_info:
            # LLM이 자연스럽게 다음 질문을 하도록 유도
            next_question_prompt = f"다음 정보가 업데이트되었습니다: {update_summary}. 다음으로 {missing_info[0][1]}에 대해 여쭤봐도 될까요?"
            return next_question_prompt
        else:
            # 모든 필수 정보 수집 시 가입 권유 또는 추가 질문 유도
            return f"다음 정보가 업데이트되었습니다: {update_summary}. 이제 고객님께 맞는 플랜을 추천해드릴 수 있을 것 같습니다. 잠시만 기다려주시겠어요?"

    def get_profile_summary(self):
        """현재 고객 프로필 요약을 반환합니다."""
        return str(self.customer_profile)

    def set_selected_product(self, product_name: str):
        """
        고객이 선택한 상품(플랜 유형)을 프로필에 설정합니다.
        (Recommendation Agent와의 연동을 위해 plan_type으로 변경 고려)
        """
        # product_name이 플랜 유형 중 하나인지 확인
        if product_name in ["고급형", "표준형", "3400형"]:
             self.customer_profile.selected_plan_type = product_name # selected_plan_type 속성 사용
             return f"'{product_name}' 플랜 유형을 고객님의 선택으로 설정했습니다."
        else:
             # 일반 상품명으로 처리하거나 오류 반환
             self.customer_profile.selected_product = product_name # 기존 selected_product도 유지할 수 있음
             return f"'{product_name}' 상품에 관심을 보이시는군요. 해당 상품/플랜에 대해 더 자세히 알아볼까요?"

    def process_purchase_interest(self):
        """
        고객의 구매 의향을 확인하고, 최종 가입 동의를 유도하거나 다음 단계를 안내합니다.
        """
        profile = self.customer_profile
        selected_plan = getattr(profile, 'selected_plan_type', None) # 플랜 유형 우선 확인

        if not selected_plan and not profile.selected_product:
             # LLM이 추천 또는 질문하도록 유도
            return "구매를 진행하시기 전에 어떤 플랜 유형이나 상품에 관심 있으신지 알려주시겠어요? 고객님께 맞는 최적의 플랜을 찾아드리겠습니다."

        # 선택된 플랜/상품 이름 결정
        target_plan_or_product = selected_plan if selected_plan else profile.selected_product

        # 최종 가입 의사 확인 및 동의 유도 프롬프트
        prompt = f"""
        고객 프로필:
        {json.dumps(profile.to_dict(), ensure_ascii=False, indent=2)}

        선택된 플랜/상품: {target_plan_or_product}

        고객이 '{target_plan_or_product}' 플랜/상품 가입에 관심을 보이고 있습니다.
        마지막으로 가입 의사를 명확히 확인하고, "네, 가입하겠습니다" 또는 유사한 긍정적인 답변을 유도하는 메시지를 작성해주세요.
        가입 시 얻게 될 주요 혜택(예: 안심하고 운전할 수 있는 든든함)을 짧게 강조하며 자연스럽게 동의를 구하세요.
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5 # 약간의 창의성 부여
            )
            # LLM이 생성한 가입 유도 메시지 반환
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error processing purchase interest: {e}")
            # 예외 발생 시 기본 가입 유도 메시지
            return f"{target_plan_or_product} 플랜/상품이 고객님께 든든한 보호막이 되어드릴 겁니다. 이 플랜으로 최종 결정하시겠어요?"

    def explain_purchase_process(self, product_name: str = None):
        """
        보험 가입 과정을 상세히 설명합니다. (가입 동의 후 설명하는 시나리오)
        """
        if not product_name:
             product_name = getattr(self.customer_profile, 'selected_plan_type', self.customer_profile.selected_product)

        if not product_name:
             # 이 단계는 보통 가입 동의 후 호출되므로 상품/플랜이 있어야 함
             return "오류: 가입 절차를 설명할 상품/플랜 정보가 없습니다."

        # 가입 절차 설명 (간결하게 핵심 위주로)
        return f"""
네, {product_name} 가입을 결정해주셔서 감사합니다! 가입 절차는 간단합니다.

1.  **온라인/모바일 청약**: 제가 보내드릴 링크를 통해 간편하게 청약서를 작성하실 수 있습니다. (또는 전화/대면 상담 안내)
2.  **필요 정보 확인**: 운전면허증 정보 등 몇 가지 정보만 확인해주시면 됩니다.
3.  **첫 보험료 결제**: 원하시는 방식으로 첫 보험료를 결제하시면 됩니다.
4.  **보장 시작**: 결제가 완료되면 즉시 또는 지정된 날짜부터 든든한 보장이 시작됩니다!

곧 가입 진행을 위한 안내를 드리겠습니다. 잠시만 기다려주세요."""

    def schedule_consultation(self, name: str, phone: str, preferred_time: str):
        """운전자보험 상담 일정을 예약합니다."""
        if name: self.customer_profile.name = name
        if phone: self.customer_profile.preferred_contact_method = f"전화 ({phone})"

        # 실제 CRM 연동 로직 대신 확인 메시지 생성
        plan_info = ""
        selected_plan = getattr(self.customer_profile, 'selected_plan_type', None)
        if selected_plan:
             plan_info = f" '{selected_plan}' 플랜에 관한"
        elif self.customer_profile.selected_product:
             plan_info = f" '{self.customer_profile.selected_product}' 상품에 관한"

        return (
            f"{name or '고객'}님의 한화손해보험 운전자보험{plan_info} 상담이 {preferred_time}으로 예약되었습니다. "
            f"{phone} 번호로 연락드리겠습니다. 감사합니다."
        )

    def transfer_to_recommendation_agent(self):
        """상품 추천이 필요할 때 추천 에이전트로 전환합니다."""
        # 추천 에이전트로 전환하기 전에 현재까지 수집된 프로필 정보를 전달하는 로직 추가 가능
        from agents.advanced_agents.recommendation_agent import AdvancedRecommendationAgent
        # 예: recommendation_agent = AdvancedRecommendationAgent()
        #     recommendation_agent.customer_profile = self.customer_profile # 프로필 전달
        #     return recommendation_agent
        print("[SalesAgent] 추천 에이전트로 전환합니다.")
        return AdvancedRecommendationAgent()

    def transfer_to_rag_agent(self):
        """고객이 상품에 대한 자세한 정보를 원할 때 RAG 에이전트로 전환합니다."""
        from agents.advanced_agents.rag_agent import AdvancedRAGAgent
        print("[SalesAgent] RAG 에이전트로 전환합니다.")
        return AdvancedRAGAgent() 