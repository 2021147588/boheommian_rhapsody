import os
from dotenv import load_dotenv
from agents.advanced_orchestrator import AdvancedOrchestrator

# 환경 변수 로드
load_dotenv()

def main():
    """
    보험 상담 에이전트 시스템 사용 예시
    """
    print("=" * 50)
    print("보험 설계 에이전트 시스템 데모")
    print("=" * 50)
    print("\n이 데모는 다음 기능을 포함하고 있습니다:")
    print("1. 라우터 에이전트: 사용자 질문을 분석하여 적절한 에이전트로 라우팅")
    print("2. RAG 에이전트: 보험 정보 검색 및 상세 정보 제공")
    print("3. 영업 에이전트: 맞춤형 상품 추천 및 상담")
    print("4. 핸드오프: 대화 문맥에 따라 자연스럽게 에이전트 전환")
    print("\n명령어:")
    print("- '종료' 또는 'exit': 프로그램 종료")
    print("- '초기화' 또는 'reset': 대화 초기화")
    print("=" * 50)
    
    # 에이전트 시스템 초기화
    orchestrator = AdvancedOrchestrator()
    
    print("\n시스템: 안녕하세요! 보험 관련 질문이나 상담이 필요하신가요?")
    
    # 대화 루프
    while True:
        user_input = input("\n사용자: ")
        
        # 종료 명령 처리
        if user_input.lower() in ["exit", "종료"]:
            print("\n시스템: 상담을 종료합니다. 감사합니다!")
            break
        
        # 초기화 명령 처리
        if user_input.lower() in ["reset", "초기화"]:
            print(f"\n시스템: {orchestrator.reset()}")
            print("\n시스템: 안녕하세요! 새로운 상담을 시작합니다. 무엇을 도와드릴까요?")
            continue
        
        # 에이전트 응답 처리
        try:
            response = orchestrator.process_message(user_input)
            print(f"\n에이전트: {response}")
        except Exception as e:
            print(f"\n시스템 오류: {str(e)}")
            print("시스템을 재시작합니다...")
            orchestrator.reset()
    
    # 대화 기록 출력
    print("\n=== 대화 기록 ===")
    for message in orchestrator.get_conversation_history():
        print(message)

if __name__ == "__main__":
    main() 