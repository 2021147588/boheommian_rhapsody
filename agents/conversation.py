from agents.advanced_planner_agents.advanced_orchestrator import AdvancedOrchestrator
from agents.user_agent.user_agent import UserAgent
from app.view import *
import json
import os
import datetime

class AgentConversation:
    def __init__(self, user_info: UserInfo, max_turns: int = 1):
        self.user_agent = UserAgent(user_info)
        self.orchestrator = AdvancedOrchestrator()
        self.chat_log = []
        self.max_turns = max_turns
        self.chat_history = ""  # 문자열 형태로 유지
        self.success = False  # 가입 성공 여부 추적
        self.user_info = user_info  # 사용자 정보 저장
        
        # 향상된 대화 로그 (턴 단위로 상세 정보 기록)
        self.enhanced_log = []

        # 사용자 정보 요약
        self.user_info_summary = f"""
            사용자 정보:
            - 이름: {user_info.user.name}
            - 나이: {user_info.user.birth_date[:4]}
            - 성별: {user_info.user.gender}
            - 운전 경력: {user_info.user.driving_experience_years}년
            - 사고 이력: {"있음" if user_info.user.accident_history else "없음"}
            - 운전 스타일: {user_info.user.driving_style}
            - 사고 이력 정보: {user_info.user.accident_history_info}
            - 보험 성향: {user_info.user.insurance_tendency}
            - 기본 옵션 기대: {user_info.user.basic_option_expectation}
            - 예상 보험 등급: {user_info.user.expected_insurance_grade}
            - 추가 참고사항: {user_info.user.additional_notes}
            - 차량 모델: {user_info.vehicle.model}
            - 사용 목적: {user_info.vehicle.usage}
            - 차량 가치: {user_info.vehicle.market_value}원
        """
                    
    def simulate_conversation(self, initial_input: str = "운전자 보험 추천해주세요."):
        print("=== 에이전트 간 자동 대화 시뮬레이션 시작 ===")
        user_message = initial_input
        self.chat_history += f"User: {initial_input}\nOrchestrator: "
        self.chat_log.append({"role": "user", "content": user_message})

        # 매번 사용자 정보를 대화 흐름에 포함시켜서 대화가 지속적으로 이어지도록
        self.chat_history = self.user_info_summary + "\n" + self.chat_history
        
        # 추천 과정 추적을 위한 변수
        recommendation_made = False
        
        for turn in range(self.max_turns):
            print(f"\n🔁 [Turn {turn+1}]")

            # 턴별 로그 초기화
            turn_log = {
                "turn": turn + 1,
                "user_reply": user_message if turn == 0 else None,  # 첫 턴에만 초기 사용자 메시지 포함
                "agent_response": None,
                "current_agent": "Router",  # 기본값, Orchestrator가 실제 에이전트 식별
                "rag_performed": False,
                "rag_sources": None
            }

            # 1. Orchestrator가 응답
            orchestrator_response = self.orchestrator.run_with_history(
                self.chat_history,
                user_message
            )
            print(f"[Orchestrator]: {orchestrator_response}")
            
            # 현재 활성화된 에이전트 추출 (로그 메시지나 응답에서 식별)
            current_agent = self._identify_current_agent(orchestrator_response)
            
            # RAG 사용 여부 및 소스 추출 (응답에서 식별)
            rag_performed, rag_sources = self._extract_rag_info(orchestrator_response)
            
            # 로그 업데이트
            turn_log["agent_response"] = orchestrator_response
            turn_log["current_agent"] = current_agent
            turn_log["rag_performed"] = rag_performed
            turn_log["rag_sources"] = rag_sources
            
            # 추천 완료 여부 확인 (표준형, 고급형, 3400형 언급이 있는지)
            if not recommendation_made and any(plan in orchestrator_response for plan in ["표준형", "고급형", "3400형"]):
                recommendation_made = True
                print("[System] 보험 플랜 추천이 완료되었습니다.")
            
            self.chat_history += f"{orchestrator_response}\nUser: "
            self.chat_log.append({"role": "orchestrator", "content": orchestrator_response})

            # 2. UserAgent가 응답
            user_response = self.user_agent.run(self.chat_history, orchestrator_response)
            print(f"[User] {user_response}")
            self.chat_log.append({"role": "user", "content": user_response})
            self.chat_history += f"{user_response}\nOrchestrator:"
            
            # 사용자 응답 로그 업데이트
            if turn != 0:  # 첫 턴이 아닌 경우에만 업데이트 (첫 턴은 이미 설정됨)
                turn_log["user_reply"] = user_response
            
            # 최종 턴 로그 저장
            self.enhanced_log.append(turn_log)

            # 3. 성공 여부 확인 - 가입 의사 확인 (단, 추천이 이루어진 이후에만)
            if recommendation_made and self._check_success(user_response):
                self.success = True
                print("✅ 성공: 고객이 보험 가입에 동의했습니다!")
                break

            user_message = user_response  # 다음 턴 입력
            
        # 최대 턴에 도달했는데 성공하지 못한 경우
        if not self.success and turn == self.max_turns - 1:
            print("❌ 실패: 최대 대화 턴에 도달했지만 고객이 가입하지 않았습니다.")
    
    def _identify_current_agent(self, response):
        """응답 내용에서 현재 활성화된 에이전트를 식별"""
        # 단계별 로그 메시지에서 일반적으로 나타나는 패턴을 확인
        agent_patterns = {
            "Router Agent:": "Router",
            "Recommendation Agent:": "Recommendation",
            "Sales Agent:": "Sales",
            "RAG Agent:": "RAG"
        }
        
        # 터미널 로그에 나타나는 메시지 확인
        for pattern, agent_type in agent_patterns.items():
            if pattern in response:
                return agent_type
                
        # 다른 키워드 기반 식별 방법 (백업)
        agent_indicators = {
            "Router": ["라우터", "메시지를 분석", "라우팅"],
            "Recommendation": ["추천 에이전트", "보험 플랜 추천", "가장 적합한 보험", "맞춤형 플랜"],
            "Sales": ["영업 담당자", "영업 에이전트", "가입 상담", "상품 가입", "할인 혜택"],
            "RAG": ["RAG 에이전트", "약관 정보", "상세 정보 검색", "문서 검색"]
        }
        
        for agent_type, keywords in agent_indicators.items():
            if any(keyword in response for keyword in keywords):
                return agent_type
        
        # Enhanced Agent 감지 - 실제 대화 내용 분석
        if "보험 플랜" in response or "보장 내용" in response or "추천드릴 상품" in response:
            return "Recommendation"
        elif "할인 혜택" in response or "가입" in response or "보험료" in response:
            return "Sales"
        elif "약관" in response or "보장 범위" in response or "법적 책임" in response:
            return "RAG"
            
        # 기본값
        return "Router"
    
    def _extract_rag_info(self, response):
        """응답에서 RAG 사용 여부와 소스 정보 추출"""
        rag_indicators = ["검색 결과:", "약관에 따르면", "찾아본 결과", "관련 정보:", "문서에 따르면"]
        
        if any(indicator in response for indicator in rag_indicators):
            # RAG 수행됨, 소스 추출 시도
            sources = None
            source_sections = []
            
            # 소스 분리 패턴 찾기
            source_patterns = [
                "검색 결과:", "참고 문서:", "출처:", "약관 내용:", "관련 정보:"
            ]
            
            for pattern in source_patterns:
                if pattern in response:
                    parts = response.split(pattern)
                    if len(parts) > 1:
                        # 소스 텍스트 추출 (다음 문단 또는 200자 제한)
                        source_text = parts[1].split("\n\n")[0] if "\n\n" in parts[1] else parts[1][:200]
                        source_sections.append(source_text.strip())
            
            if source_sections:
                sources = "; ".join(source_sections)
                # 긴 소스는 요약
                if len(sources) > 300:
                    sources = sources[:297] + "..."
            
            return True, sources
        
        return False, None
    
    def _check_success(self, user_message):
        """사용자 메시지에서 가입 의사가 있는지 확인"""
        positive_indicators = [
            "가입하겠습니다", "가입할게요", "신청합니다", "동의합니다", "좋아요, 가입할게요",
            "계약하겠습니다", "결정했어요", "진행해주세요", "신청서 작성할게요",
            "구매하겠습니다", "알겠습니다, 가입할게요", "신청해 볼게요"
        ]
        
        return any(indicator in user_message for indicator in positive_indicators)

    def get_conversation_dict(self):
        """대화 내용을 발화 순서대로 딕셔너리 형태로 반환"""
        conversation_dict = {
                "user_info": {
                        **self.user_info.model_dump()  # model_dump() 결과를 언팩하여 딕셔너리로 포함
                    },
            "success": self.success,
            "exchanges": []
        }
        
        # 대화 내용을 순서대로 추가
        turn_number = 1
        user_turn = True
        current_exchange = {"turn": turn_number, "user": "", "agent": ""}
        
        for message in self.chat_log:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                if not user_turn and current_exchange["user"] and current_exchange["agent"]:
                    # 이전 교환이 완료되었고 새로운 유저 턴이 시작됨
                    conversation_dict["exchanges"].append(current_exchange)
                    turn_number += 1
                    current_exchange = {"turn": turn_number, "user": content, "agent": ""}
                else:
                    # 첫 번째 유저 메시지 또는 같은 턴의 계속
                    current_exchange["user"] = content
                user_turn = False
            elif role == "orchestrator":
                current_exchange["agent"] = content
                user_turn = True
        
        # 마지막 교환 추가
        if current_exchange["user"] or current_exchange["agent"]:
            conversation_dict["exchanges"].append(current_exchange)
            
        return conversation_dict

    def get_simplified_conversation(self):
        """발화만 추출한 간단한 대화 포맷으로 반환"""
        exchanges = []
        turn_number = 0
        
        for i in range(0, len(self.chat_log)):
            message = self.chat_log[i]
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                exchanges.append({
                    "speaker": "user",
                    "text": content,
                    "turn": turn_number
                })
            elif role == "orchestrator":
                turn_number += 1
                exchanges.append({
                    "speaker": "agent",
                    "text": content,
                    "turn": turn_number
                })
                
        return {
            "user_name": self.user_info.user.name,
            "success": self.success,
            "dialogue": exchanges
        }
    
    def get_enhanced_log(self):
        """턴 단위로 저장된 상세 로그 반환"""
        return {
            "user_info": self.user_info.model_dump(),  # model_dump() 결과를 언팩하여 딕셔너리로 포함
            
            "success": self.success,
            "turns": self.enhanced_log
        }

if __name__ == "__main__":
    
    user_info_json_path = "person.json"
    with open(user_info_json_path, "r", encoding="utf-8") as file:
        user_info_list = json.load(file)

    detailed_chat_log = []
    simplified_chat_log = []
    enhanced_chat_log = []  # 새로운 향상된 로그
    success_count = 0
    total_samples = min(len(user_info_list), 1)  # 처음 1개 샘플만 테스트
    
    # results 디렉토리 생성
    results_dir = "agents/results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"'{results_dir}' 디렉토리를 생성했습니다.")
    
    # 타임스탬프로 파일명 생성
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, user_info_dict in enumerate(user_info_list[:total_samples]):
        print(f"\n===== 시뮬레이션 {i+1}/{total_samples} =====")
        user_info = UserInfo(**user_info_dict)
        conversation = AgentConversation(user_info)
        conversation.simulate_conversation()
        
        # 성공 여부 집계
        if conversation.success:
            success_count += 1
            
        # 상세 대화 내용 저장 (메모리에만 저장, 파일 저장 안 함)
        detailed_data = conversation.get_conversation_dict()
        detailed_chat_log.append(detailed_data)
        
        # 간소화된 대화 내용 저장 (메모리에만 저장, 파일 저장 안 함)
        simplified_data = conversation.get_simplified_conversation()
        simplified_chat_log.append(simplified_data)
        
        # 향상된 로그 저장
        enhanced_data = conversation.get_enhanced_log()
        enhanced_chat_log.append(enhanced_data)
        
        # 개별 파일 저장 - enhanced 로그만 저장
        user_name = user_info.user.name
        user_id = f"user_{i+1}"
        
        # # 향상된 로그 버전 저장 (enhanced만 저장)
        # enhanced_filename = f"{results_dir}/{timestamp}_{user_id}_{user_name}_enhanced.json"
        # with open(enhanced_filename, "w", encoding='utf-8') as file:
        #     json.dump(enhanced_data, file, ensure_ascii=False, indent=4)
        #     print(f"향상된 로그를 '{enhanced_filename}' 파일에 저장했습니다.")
    
    # 결과 출력
    print(f"\n===== 시뮬레이션 결과 =====")
    print(f"총 샘플: {total_samples}")
    print(f"성공 샘플: {success_count}")
    print(f"성공률: {success_count/total_samples*100:.1f}%")
    
    # 모든 대화 통합 파일 저장 (향상된 로그 버전만)
    enhanced_all_file = f"{results_dir}/{timestamp}_all_enhanced.json"
    with open(enhanced_all_file, "w", encoding='utf-8') as file:
        json.dump({
            "summary": {
                "total_samples": total_samples,
                "success_count": success_count,
                "success_rate": success_count/total_samples*100
            },
            "conversations": enhanced_chat_log
        }, file, ensure_ascii=False, indent=4)
        print(f"모든 향상된 로그를 '{enhanced_all_file}' 파일에 저장했습니다.")



    # except Exception as e:
    #     with open("chat_log.json", "w", encoding='utf-8') as file:
    #         json.dump(total_chat_log, file, ensure_ascii=False, indent=4)
        