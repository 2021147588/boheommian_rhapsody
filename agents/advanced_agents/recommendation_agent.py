from agents.planner_agent.advanced_base_agent import AdvancedBaseAgent
import os
import json
from openai import OpenAI
from typing import List, Dict, Any

class InsuranceProductDB:
    """
    운전자보험 상품 데이터베이스
    실제로는 외부 DB에서 가져오는 로직이 필요할 수 있음
    """
    def __init__(self):
        self.products = {
            "차도리운전자보험": {
                "name": "차도리운전자보험",
                "description": "기본적인 보장을 제공하는 표준 상품",
                "target_age": "전 연령",
                "target_experience": "제한 없음",
                "price_range": "월 10,000원~20,000원",
                "coverage": {
                    "교통사고처리지원금": "최대 3천만원",
                    "벌금": "최대 2천만원",
                    "변호사선임비용": "최대 500만원",
                    "자동차사고부상치료비": "최대 1천만원",
                    "면허정지위로금": "1일당 1만원(최대 120일)"
                }
            },
            "차도리운전자보험Plus": {
                "name": "차도리운전자보험Plus",
                "description": "보장 범위가 확대된 프리미엄 상품",
                "target_age": "30~60세",
                "target_experience": "3년 이상",
                "price_range": "월 15,000원~30,000원",
                "coverage": {
                    "교통사고처리지원금": "최대 1억원",
                    "벌금": "최대 5천만원",
                    "변호사선임비용": "최대 1천만원",
                    "자동차사고부상치료비": "최대 2천만원",
                    "면허정지위로금": "1일당 2만원(최대 120일)",
                    "면허취소위로금": "최대 100만원",
                    "교통상해입원일당": "1일당 3만원(최대 180일)"
                }
            },
            "차도리ECO운전자보험": {
                "name": "차도리ECO운전자보험",
                "description": "친환경 차량 특화 상품",
                "target_age": "20~50세",
                "target_experience": "제한 없음",
                "vehicle_type": "하이브리드, 전기차",
                "price_range": "월 12,000원~25,000원",
                "coverage": {
                    "교통사고처리지원금": "최대 5천만원",
                    "벌금": "최대 3천만원",
                    "변호사선임비용": "최대 700만원",
                    "자동차사고부상치료비": "최대 1천만원",
                    "면허정지위로금": "1일당 1만5천원(최대 120일)",
                    "친환경차충전중상해": "최대 1천만원",
                    "친환경차배터리교체비용": "최대 200만원"
                }
            },
            "차도리운전자보험VIP": {
                "name": "차도리운전자보험VIP",
                "description": "최고 수준의 보장을 제공하는 프리미엄 상품",
                "target_age": "30~65세",
                "target_experience": "5년 이상",
                "price_range": "월 25,000원~50,000원",
                "coverage": {
                    "교통사고처리지원금": "최대 2억원",
                    "벌금": "최대 7천만원",
                    "변호사선임비용": "최대 2천만원",
                    "자동차사고부상치료비": "최대 3천만원",
                    "면허정지위로금": "1일당 3만원(최대 120일)",
                    "면허취소위로금": "최대 200만원",
                    "교통상해입원일당": "1일당 5만원(최대 180일)",
                    "자동차사고성형수술비": "최대 500만원",
                    "운전중교통상해사망": "최대 5천만원"
                }
            }
        }
    
    def get_product(self, product_id):
        """특정 상품 정보 조회"""
        return self.products.get(product_id)
    
    def get_all_products(self):
        """모든 상품 정보 조회"""
        return self.products
    
    def search_products(self, keywords):
        """키워드 기반 상품 검색"""
        result = {}
        for product_id, product in self.products.items():
            for keyword in keywords:
                if (keyword.lower() in product_id.lower() or 
                    keyword.lower() in product["description"].lower()):
                    result[product_id] = product
                    break
        return result

class AdvancedRecommendationAgent(AdvancedBaseAgent):
    def __init__(self):
        # 상품 DB 초기화
        self.product_db = InsuranceProductDB()
        
        # OpenAI 클라이언트 초기화
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        super().__init__(
            name="Recommendation Agent",
            system_message=(
                "당신은 한화손해보험의 운전자보험 추천 전문가입니다. 다음 지침에 따라 고객을 응대하세요:\n"
                "1. 제공된 고객 프로필 정보를 바탕으로 최적의 운전자보험 상품을 추천합니다.\n"
                "2. 보장 내용, 보험료, 특약 등을 고객의 상황에 맞게 맞춤형으로 설명합니다.\n"
                "3. 여러 상품의 비교 분석을 제공하여 고객이 최선의 선택을 할 수 있도록 돕습니다.\n"
                "4. 추천 과정에서 필요한 추가 정보가 있다면 질문을 통해 수집합니다.\n"
                "5. 상품 추천을 완료한 후에는 즉시 영업 에이전트로 전환하여 가입 상담을 진행합니다.\n"
                "항상 객관적이고 정확한 정보를 제공하되, 실제 가입 상담은 영업 에이전트가 담당하도록 합니다."
            ),
            model="gpt-4o-mini",
            tools=[
                self.recommend_insurance,
                self.generate_next_questions,
                self.get_product_details,
                self.compare_products,
                self.transfer_to_sales_agent,
                self.transfer_to_rag_agent
            ]
        )
    
    def recommend_insurance(self, profile_data: str):
        """
        고객 프로필을 기반으로 운전자보험 상품을 추천합니다.
        
        Args:
            profile_data: 고객 프로필 정보 (JSON 문자열)
            
        Returns:
            str: 추천 상품 정보
        """
        try:
            # 프로필 정보 파싱
            profile = json.loads(profile_data)
            
            # 상품 DB에서 정보 가져오기
            all_products = self.product_db.get_all_products()
            products_info = json.dumps(all_products, ensure_ascii=False)
            
            # 프롬프트 구성
            prompt = f"""
            고객의 프로필 정보와 가용한 보험 상품 목록을 분석하여, 가장 적합한 운전자보험 상품을 추천해주세요.
            
            고객 프로필:
            {json.dumps(profile, ensure_ascii=False, indent=2)}
            
            가용한 보험 상품:
            {products_info}
            
            다음 형식으로 추천해주세요:
            1. 추천 상품명
            2. 추천 이유 (고객 프로필과의 관련성)
            3. 핵심 보장 내용 (3-5가지)
            4. 월 예상 보험료 범위
            5. 추가 고려사항이나 특이점
            
            자연스러운 대화 형식으로 추천을 작성하고, 마지막에 "이제 영업 담당자가 상품 가입에 대해 더 자세히 안내해 드리겠습니다."라는 문구로 마무리해주세요.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            recommendation = response.choices[0].message.content
            
            # 영업 에이전트로 전환
            # 추천 결과를 반환하고, 오케스트레이터에서 이 응답이 처리된 후
            # 바로 다음 스텝에서 영업 에이전트로 전환되도록 함
            from agents.advanced_agents.sales_agent import AdvancedSalesAgent
            sales_agent = AdvancedSalesAgent()
            
            # 추천된 상품을 추출해서 영업 에이전트에 전달
            try:
                import re
                recommended_product = None
                product_match = re.search(r'추천(?:드리는|해드리는|하는)?\s+(?:상품은|상품)\s+[\'"]?(차도리[^\'"\n]+)[\'"]?', recommendation)
                if product_match:
                    recommended_product = product_match.group(1).strip()
                    if recommended_product:
                        sales_agent.customer_profile.selected_product = recommended_product
                        print(f"[RecommendationAgent] 추천 상품 '{recommended_product}'을(를) 영업 에이전트에 전달합니다.")
            except Exception as e:
                print(f"[RecommendationAgent] 추천 상품 추출 오류: {e}")
            
            return recommendation + "\n\nHANDOFF_TO_SALES_AGENT"
            
        except Exception as e:
            print(f"Error recommending insurance: {e}")
            return "추천 생성 중 오류가 발생했습니다. 정확한 고객 프로필 정보가 필요합니다."
    
    def generate_next_questions(self, profile_data: str):
        """
        고객 프로필에서 누락된 정보를 수집하기 위한 질문을 생성합니다.
        
        Args:
            profile_data: 고객 프로필 정보 (JSON 문자열)
            
        Returns:
            str: 추천 질문 목록
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
                'current_driver_insurance': '현재 운전자보험 가입 여부'
            }
            
            # 누락된 필드 확인
            missing_fields = []
            for field, display_name in critical_fields.items():
                if field not in profile or profile[field] is None:
                    missing_fields.append(display_name)
            
            # 프롬프트 구성
            prompt = f"""
            현재 고객 프로필 정보를 기반으로, 운전자보험 추천을 위해 필요한 추가 질문을 생성해주세요.
            질문은 자연스러운 대화 형식으로 생성하고, 고객이 아직 제공하지 않은 정보를 수집하는 데 중점을 두어야 합니다.

            현재 프로필 정보:
            {json.dumps(profile, ensure_ascii=False, indent=2)}

            특히 다음 정보가 누락된 경우 관련 질문을 생성하세요:
            {', '.join(missing_fields) if missing_fields else "모든 필수 정보가 수집되었습니다."}

            3-5개의 간결하고 구체적인 질문을 생성해주세요. 질문은 일상 대화처럼 자연스럽게 작성해주세요.
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
    
    def get_product_details(self, product_id: str):
        """
        특정 보험 상품의 상세 정보를 반환합니다.
        
        Args:
            product_id: 상품 ID
            
        Returns:
            str: 상품 상세 정보
        """
        product = self.product_db.get_product(product_id)
        
        if not product:
            return f"'{product_id}' 상품을 찾을 수 없습니다. 다음 상품 중 하나를 선택해주세요: {', '.join(self.product_db.get_all_products().keys())}"
        
        # 상품 정보 포맷팅
        product_info = f"## {product['name']}\n\n"
        product_info += f"**설명**: {product['description']}\n\n"
        product_info += f"**대상 연령**: {product['target_age']}\n"
        product_info += f"**필요 운전 경력**: {product['target_experience']}\n"
        product_info += f"**월 보험료 범위**: {product['price_range']}\n\n"
        
        product_info += "**보장 내용**:\n"
        for coverage, amount in product['coverage'].items():
            product_info += f"- {coverage}: {amount}\n"
        
        return product_info
    
    def compare_products(self, product_ids: List[str]):
        """
        여러 보험 상품을 비교합니다.
        
        Args:
            product_ids: 비교할 상품 ID 목록
            
        Returns:
            str: 상품 비교 결과
        """
        products = []
        missing_products = []
        
        # 존재하는 상품 확인
        for product_id in product_ids:
            product = self.product_db.get_product(product_id)
            if product:
                products.append(product)
            else:
                missing_products.append(product_id)
        
        if not products:
            all_products = list(self.product_db.get_all_products().keys())
            return f"요청하신 상품을 찾을 수 없습니다. 다음 상품 중에서 선택해주세요: {', '.join(all_products)}"
        
        # 비교 결과 생성 프롬프트
        product_data = json.dumps(products, ensure_ascii=False, indent=2)
        
        prompt = f"""
        다음 운전자보험 상품들을 비교 분석해주세요:
        
        {product_data}
        
        다음 형식으로 상품 비교 결과를 제공해주세요:
        1. 가격 비교
        2. 보장 범위 비교
        3. 대상 고객층 비교
        4. 각 상품의 장단점
        5. 어떤 상황에 어떤 상품이 적합한지 안내
        
        자연스러운 설명문으로 작성해주세요.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            comparison = response.choices[0].message.content
            
            # 찾을 수 없는 상품 안내 추가
            if missing_products:
                comparison += f"\n\n참고: 요청하신 '{', '.join(missing_products)}' 상품은 찾을 수 없어 비교에서 제외되었습니다."
                
            return comparison
            
        except Exception as e:
            print(f"Error comparing products: {e}")
            return "상품 비교 중 오류가 발생했습니다."
    
    def transfer_to_sales_agent(self):
        """
        고객이 상품 가입이나 상담을 원할 때 영업 에이전트로 전환합니다.
        """
        from agents.advanced_agents.sales_agent import AdvancedSalesAgent
        return AdvancedSalesAgent()
    
    def transfer_to_rag_agent(self):
        """
        고객이 상품에 대한 자세한 정보를 원할 때 RAG 에이전트로 전환합니다.
        """
        from agents.advanced_agents.rag_agent import AdvancedRAGAgent
        return AdvancedRAGAgent() 