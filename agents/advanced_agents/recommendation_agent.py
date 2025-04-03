from agents.planner_agent.advanced_base_agent import AdvancedBaseAgent
import os
import json
from openai import OpenAI
from typing import List, Dict, Any, Tuple
import re

class InsuranceProductDB:
    """
    운전자보험 상품 데이터베이스 (플랜 유형 및 보장 금액 기반)
    '고급형', '표준형', '3400형' 플랜과 각 플랜에 포함된 옵션 및 보장 금액 정보를 관리합니다.
    """
    def __init__(self):
        self.plan_types = ["고급형", "표준형", "3400형"]
        # 각 보장 옵션별 상세 정보 (플랜별 금액 포함)
        # '-' 는 해당 플랜에서 제공되지 않음을 의미
        self.coverage_details = {
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
        }

    def get_plan_details(self, plan_type: str) -> Dict[str, Any] | None:
        """특정 보험 플랜의 상세 정보 (보장명과 금액 포함)를 반환합니다."""
        if plan_type not in self.plan_types:
            return None

        plan_details = {
            "name": plan_type,
            "description": f"{plan_type} 운전자보험 플랜입니다.",
            "coverages": [] # (보장명, 금액) 튜플 리스트
            # 필요시 가격 범위, 대상 연령 등 추가 정보 포함 가능
        }
        for option_name, details in self.coverage_details.items():
            amount = details.get(plan_type)
            # 금액이 '-' 가 아닌 경우에만 포함
            if amount and amount != '-':
                plan_details["coverages"].append((option_name, amount))

        return plan_details

    def get_all_plan_details(self) -> Dict[str, Dict[str, Any]]:
         """모든 보험 플랜의 상세 정보 (보장명과 금액 포함)를 딕셔너리로 반환합니다."""
         all_details = {}
         for plan_type in self.plan_types:
             details = self.get_plan_details(plan_type)
             if details:
                 # coverages를 {보장명: 금액} 딕셔너리로 변환하여 저장 (프롬프트 가독성 향상)
                 details["coverages_dict"] = {name: amt for name, amt in details["coverages"]}
                 del details["coverages"] # 원래 리스트는 제거
                 all_details[plan_type] = details
         return all_details

    def get_all_plan_types(self) -> List[str]:
         """사용 가능한 모든 플랜 유형의 이름을 리스트로 반환합니다."""
         return self.plan_types

    def search_coverages(self, keywords: List[str]) -> Dict[str, Dict[str, str]]:
        """
        키워드를 포함하는 보장 옵션과 해당 옵션을 제공하는 플랜 및 금액을 검색합니다.

        Args:
            keywords: 검색할 키워드 리스트

        Returns:
            Dict[str, Dict[str, str]]: {보장 옵션명: {플랜유형1: 금액1, ...}} 형태의 딕셔너리
        """
        results = {}
        for option_name, details in self.coverage_details.items():
            # 키워드 중 하나라도 옵션명 또는 설명에 포함되는지 확인 (대소문자 구분 없음)
            search_text = option_name + details.get("description", "")
            if any(kw.lower() in search_text.lower() for kw in keywords):
                included_plans = {}
                for plan_type in self.plan_types:
                    amount = details.get(plan_type)
                    if amount and amount != '-':
                        included_plans[plan_type] = amount
                if included_plans:
                    results[option_name] = included_plans
        return results

class AdvancedRecommendationAgent(AdvancedBaseAgent):
    def __init__(self):
        # 상품 DB 초기화 (플랜 유형 및 금액 기반)
        self.product_db = InsuranceProductDB()

        # OpenAI 클라이언트 초기화
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        super().__init__(
            name="Recommendation Agent",
            system_message=(
                "당신은 한화손해보험의 운전자보험 추천 전문가입니다. 다음 지침에 따라 고객을 응대하세요:\n"
                "1. 제공된 고객 프로필 정보를 바탕으로 최적의 운전자보험 **플랜 유형(고급형, 표준형, 3400형)**과 해당 플랜의 **주요 보장 및 금액**을 고려하여 추천합니다. (recommend_insurance_plan 함수 사용)\n"
                "2. 각 플랜 유형에 포함된 보장 내용과 **금액**을 고객의 상황에 맞게 설명합니다. (get_plan_details 함수 사용)\n"
                "3. 여러 플랜 유형의 **보장 내용과 금액**을 비교 분석하여 고객이 최선의 선택을 할 수 있도록 돕습니다. (compare_plan_types 함수 사용)\n"
                "4. 추천 과정에서 필요한 추가 정보가 있다면 질문을 통해 수집합니다. (generate_next_questions 함수 사용)\n"
                "5. 플랜 유형 추천을 완료한 후에는 즉시 영업 에이전트로 전환하여 가입 상담을 진행합니다. (transfer_to_sales_agent 함수 사용)\n"
                "6. 고객이 약관이나 세부 보장 내용에 대한 자세한 정보를 요청할 경우 RAG 에이전트로 전환합니다. (transfer_to_rag_agent 함수 사용)\n"
                "항상 객관적이고 정확한 정보를 제공하되, 실제 가입 상담은 영업 에이전트가 담당하도록 합니다.\n\n"
            ),
            model="gpt-4o-mini",
            tools=[
                self.recommend_insurance_plan,
                self.generate_next_questions,
                self.get_plan_details,
                self.compare_plan_types,
                self.transfer_to_sales_agent,
                self.transfer_to_rag_agent
            ]
        )

    def recommend_insurance_plan(self, profile_data: str):
        """
        고객 프로필을 기반으로 최적의 운전자보험 플랜 유형(고급형, 표준형, 3400형)과 주요 보장 금액을 고려하여 추천합니다.

        Args:
            profile_data: 고객 프로필 정보 (JSON 문자열)

        Returns:
            AdvancedSalesAgent: 플랜 정보가 설정된 영업 에이전트 객체
        """
        try:
            # 프로필 정보 파싱
            profile = json.loads(profile_data)

            # 플랜 DB에서 정보 가져오기 (보장:금액 딕셔너리 포함)
            all_plans_details = self.product_db.get_all_plan_details()
            # JSON 직렬화 시 Tuple을 List로 변환하거나, 여기서는 이미 Dict로 변환했으므로 문제 없음
            plans_info = json.dumps(all_plans_details, ensure_ascii=False, indent=2)

            # 프롬프트 구성 (플랜 유형 및 보장 금액 기반으로 수정)
            prompt = f"""
            고객의 프로필 정보와 가용한 보험 플랜 유형 및 각 플랜의 상세 보장 내용과 금액을 분석하여, 가장 적합한 운전자보험 플랜 유형을 추천해주세요.

            고객 프로필:
            {json.dumps(profile, ensure_ascii=False, indent=2)}

            가용한 보험 플랜 유형 및 주요 보장 내용과 금액:
            (아래 `coverages_dict`는 '보장명: 보장금액' 형식입니다)
            {plans_info}

            다음 형식으로 추천해주세요:
            1. 추천 플랜 유형 (고급형, 표준형, 3400형 중 하나)
            2. 추천 이유 (고객 프로필과의 관련성 및 해당 플랜의 특징, 주요 보장 금액 수준 언급)
            3. 해당 플랜의 핵심 보장 내용과 **금액** (3-5가지, 금액 명시)
            4. 추가 고려사항이나 특이점 (예: 특정 옵션의 높은 보장 금액 또는 미포함 등)

            자연스러운 대화 형식으로 추천을 작성하고, 마지막에 "이제 영업 담당자가 상품 가입에 대해 더 자세히 안내해 드리겠습니다."라는 문구로 마무리해주세요.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            recommendation = response.choices[0].message.content

            # 플랜 유형 추출을 위한 추가 LLM 호출
            extracted_plan = None
            try:
                extraction_prompt = f"""
                다음 텍스트는 운전자 보험 플랜 추천 내용입니다.
                이 텍스트에서 최종적으로 추천하는 플랜 유형 이름 ('고급형', '표준형', '3400형' 중 하나)만 정확히 추출하여 단어 하나로 응답해주세요. 다른 설명은 포함하지 마세요.

                추천 내용:
                {recommendation}

                추천된 플랜 유형:
                """
                extraction_response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0.0,
                    max_tokens=10
                )
                extracted_plan_raw = extraction_response.choices[0].message.content.strip().replace("'", "").replace('"', '')

                # 유효한 플랜 유형인지 확인
                valid_plans = self.product_db.get_all_plan_types()
                if extracted_plan_raw in valid_plans:
                    extracted_plan = extracted_plan_raw
                else:
                    print(f"[RecommendationAgent] 경고: LLM이 유효하지 않은 플랜 유형 '{extracted_plan_raw}'을(를) 추출했습니다.")
            except Exception as e:
                print(f"[RecommendationAgent] LLM을 통한 추천 플랜 유형 추출 오류: {e}")

            # 플랜 유형 정보를 클래스 변수에 저장 (전역 상태로 유지)
            self.recommended_plan_type = extracted_plan if extracted_plan else None
            
            # 영업 에이전트 생성 및 설정
            from agents.advanced_agents.sales_agent import AdvancedSalesAgent
            sales_agent = AdvancedSalesAgent()
            
            # 추출된 플랜 유형 정보 전달
            if extracted_plan:
                try:
                    if hasattr(sales_agent, 'customer_profile') and hasattr(sales_agent.customer_profile, 'selected_plan_type'):
                        sales_agent.customer_profile.selected_plan_type = extracted_plan
                        print(f"[RecommendationAgent] 추천 플랜 유형 '{extracted_plan}'을(를) 영업 에이전트에 전달합니다.")
                except Exception as e:
                    print(f"[RecommendationAgent] 영업 에이전트에 플랜 유형 설정 중 오류: {e}")
            
            # 추천 내용을 sales_agent에 정보로 저장 (필요시)
            if hasattr(sales_agent, 'last_recommendation'):
                sales_agent.last_recommendation = recommendation
            
            # AdvancedBaseAgent 객체를 반환하여 핸드오프 처리
            # run_interaction 메서드가 이를 자동으로 감지하고 처리함
            return sales_agent

        except Exception as e:
            print(f"Error recommending insurance plan: {e}")
            # 오류 발생 시 None 반환 (핸드오프 발생하지 않음)
            return "플랜 추천 생성 중 오류가 발생했습니다. 정확한 고객 프로필 정보가 필요합니다."

    def generate_next_questions(self, profile_data: str):
        """
        고객 프로필에서 누락된 정보를 수집하기 위한 질문을 생성합니다.
        (이 함수는 플랜 유형 구조 변경과 직접적인 관련은 없으므로 기존 로직 유지)
        """
        try:
            # 프로필 정보 파싱
            profile = json.loads(profile_data)

            # 필수 필드 정의
            critical_fields = {
                'age': '고객님의 연령대',
                'driving_experience': '운전 경력',
                'vehicle_type': '차량 종류',
                'commute_distance': '출퇴근 거리',
                'current_driver_insurance': '현재 운전자보험 가입 여부',
                'desired_coverage_level': '선호하는 보장 수준(예: 기본, 표준, 포괄적)', # 추가적인 질문 필드 예시
                'budget_range': '월 보험료 예산 범위' # 추가적인 질문 필드 예시
            }

            # 누락된 필드 확인
            missing_fields = []
            for field, display_name in critical_fields.items():
                if field not in profile or not profile.get(field):
                    missing_fields.append(display_name)

            if not missing_fields:
                 return "운전자 보험 추천을 위한 정보가 충분히 모인 것 같습니다. 어떤 플랜 유형을 추천해 드릴까요?"


            # 프롬프트 구성
            prompt = f"""
            현재 고객 프로필 정보를 기반으로, 운전자보험 플랜 유형(고급형, 표준형, 3400형) 및 적정 보장 금액 추천에 필요한 추가 질문을 생성해주세요.
            질문은 자연스러운 대화 형식으로 생성하고, 고객이 아직 제공하지 않은 정보를 수집하는 데 중점을 두어야 합니다.

            현재 프로필 정보:
            {json.dumps(profile, ensure_ascii=False, indent=2)}

            특히 다음 정보가 누락되었거나 추가 정보가 필요합니다. 관련 질문을 생성하세요:
            {', '.join(missing_fields)}

            1-3개의 간결하고 구체적인 질문을 생성해주세요. 특히 예산이나 원하는 보장 수준에 대한 질문이 포함되면 좋습니다. 질문은 일상 대화처럼 자연스럽게 작성해주세요.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating questions: {e}")
            return "질문 생성 중 오류가 발생했습니다. 정확한 고객 프로필 정보가 필요합니다."


    def get_plan_details(self, plan_type: str):
        """
        특정 보험 플랜 유형(고급형, 표준형, 3400형)의 상세 정보 (보장명과 금액 포함)를 반환합니다. (Tool 용)

        Args:
            plan_type: 플랜 유형 이름 ('고급형', '표준형', '3400형')

        Returns:
            str: 플랜 상세 정보 (포맷팅된 문자열)
        """
        plan = self.product_db.get_plan_details(plan_type) # (보장명, 금액) 튜플 리스트 포함

        if not plan:
            available_plans = ', '.join(self.product_db.get_all_plan_types())
            return f"'{plan_type}' 플랜 유형을 찾을 수 없습니다. 다음 플랜 유형 중 하나를 선택해주세요: {available_plans}"

        # 플랜 정보 포맷팅 (금액 포함)
        plan_info = f"## {plan['name']} 플랜\n\n"
        plan_info += f"**설명**: {plan['description']}\n\n"
        # plan_info += f"**월 보험료 범위**: {plan.get('price_range', '별도 문의')}\n\n" # 필요시 추가

        plan_info += "**주요 보장 내용 및 금액**:\n"
        if plan['coverages']:
            for coverage_name, amount in plan['coverages']:
                plan_info += f"- {coverage_name}: **{amount}**\n" # 금액 강조
        else:
            plan_info += "- 포함된 보장 내용 정보가 없습니다.\n"

        return plan_info

    def compare_plan_types(self, plan_types: List[str]):
        """
        여러 보험 플랜 유형의 보장 내용과 금액을 비교합니다. (Tool 용)

        Args:
            plan_types: 비교할 플랜 유형 이름 목록 (예: ['고급형', '표준형'])

        Returns:
            str: 플랜 유형 비교 결과 (포맷팅된 문자열)
        """
        plans_data = []
        missing_plans = []
        valid_plan_types = self.product_db.get_all_plan_types()

        # 존재하는 플랜 유형 확인 및 데이터 수집 (보장:금액 딕셔너리 포함)
        all_details = self.product_db.get_all_plan_details()
        for plan_type in plan_types:
            if plan_type in all_details:
                plans_data.append(all_details[plan_type])
            else:
                missing_plans.append(plan_type)

        if not plans_data:
            return f"유효한 플랜 유형을 찾을 수 없습니다. 다음 중에서 선택해주세요: {', '.join(valid_plan_types)}"

        # 비교 결과 생성 프롬프트 (보장 금액 비교 강조)
        plans_json = json.dumps(plans_data, ensure_ascii=False, indent=2)

        prompt = f"""
        다음 운전자보험 플랜 유형들을 **보장 내용과 금액** 중심으로 비교 분석해주세요:
        (아래 `coverages_dict`는 '보장명: 보장금액' 형식입니다)

        {plans_json}

        다음 형식으로 플랜 유형 비교 결과를 제공해주세요:
        1. 각 플랜 유형의 주요 특징 및 대상 고객 요약 (금액 수준 언급)
        2. **주요 보장 항목별 금액 비교** (예: '자동차사고변호사선임비용Ⅴ'는 모든 플랜 OOO만원 동일, '교통상해사망'은 표준형 OOO만원, 3400형 OOO만원 등 명확히 비교)
        3. 각 플랜 유형의 장단점 (보장 범위 및 금액 수준 고려)
        4. 어떤 상황이나 예산에 어떤 플랜 유형이 더 적합할 수 있는지 안내

        자연스러운 설명문으로 작성해주세요.
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            comparison = response.choices[0].message.content

            if missing_plans:
                comparison += f"\n\n참고: 요청하신 '{', '.join(missing_plans)}' 플랜 유형은 찾을 수 없어 비교에서 제외되었습니다."

            return comparison

        except Exception as e:
            print(f"Error comparing plan types: {e}")
            return "플랜 유형 비교 중 오류가 발생했습니다."

    def transfer_to_sales_agent(self):
        """
        고객이 상품 가입이나 상담을 원할 때 영업 에이전트로 전환합니다.
        """
        from agents.advanced_agents.sales_agent import AdvancedSalesAgent
        sales_agent = AdvancedSalesAgent()
        
        # 추출한 플랜 유형 정보가 있으면 영업 에이전트에 전달
        if hasattr(self, 'recommended_plan_type') and self.recommended_plan_type:
            try:
                if hasattr(sales_agent, 'customer_profile') and hasattr(sales_agent.customer_profile, 'selected_plan_type'):
                    sales_agent.customer_profile.selected_plan_type = self.recommended_plan_type
                    print(f"[RecommendationAgent] 추천 플랜 유형 '{self.recommended_plan_type}'을(를) 영업 에이전트에 전달합니다.")
            except Exception as e:
                print(f"[RecommendationAgent] 영업 에이전트에 플랜 유형 설정 중 오류: {e}")
                
        return sales_agent


    def transfer_to_rag_agent(self):
        """
        고객이 보장 내용 등 약관에 대한 상세 정보를 원할 때 RAG 에이전트로 전환합니다.
        """
        from agents.advanced_agents.rag_agent import AdvancedRAGAgent
        return AdvancedRAGAgent() 