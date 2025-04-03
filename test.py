#!/usr/bin/env python
"""
Interactive Agent System Client

This script provides a console-based interactive interface to
interact with the multi-agent system that uses agent handoffs.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from agents.core.app import get_app

# Load environment variables
load_dotenv()

# Configure logging
def log(message, level="INFO"):
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

async def main():
    """Run the interactive agent system."""
    print("\n===== 한화손해보험 AI 상담 시스템 =====")
    print("대화를 시작합니다.")
    print("특별 명령어:")
    print("  - 'exit' 또는 'quit': 대화 종료")
    print("  - 'reset': 대화 기록 및 프로필 초기화")
    print("  - 'agent': 현재 활성화된 에이전트 확인")
    print("  - 'profile': 현재 고객 프로필 정보 확인")
    print("  - 'question': 다음 질문 추천 받기")
    print("  - 'recommend': 상품 추천 받기")
    print("  - 'debug': 디버그 정보 토글 (상세 로깅)")
    print("  - 'rag analysis': 현재 입력에 대한 RAG 분석 결과 보기\n")
    
    # Initialize the agent system
    try:
        app = get_app()
        log("에이전트 시스템 초기화 완료")
    except Exception as e:
        log(f"에이전트 시스템 초기화 중 오류 발생: {str(e)}", "ERROR")
        return
    
    # Debugging configuration
    debug_mode = True
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("\n> ")
        
        # Process special commands
        if user_input.lower() in ["exit", "quit"]:
            print("대화를 종료합니다.")
            break
            
        elif user_input.lower() == "reset":
            app.reset_conversation()
            log("대화 기록과 프로필이 초기화되었습니다.")
            continue
            
        elif user_input.lower() == "agent":
            current_agent = app.get_current_agent()
            log(f"현재 활성화된 에이전트: {current_agent}")
            continue
            
        elif user_input.lower() == "profile":
            profile_summary = app.get_profile_summary()
            print(f"\n현재 고객 프로필:\n{profile_summary}")
            continue
            
        elif user_input.lower() == "debug":
            debug_mode = not debug_mode
            log(f"디버그 모드: {'켜짐' if debug_mode else '꺼짐'}")
            continue
            
        elif user_input.lower() == "rag analysis":
            log("RAG 분석을 수행 중...")
            last_message = input("분석할 메시지를 입력하세요: ")
            if last_message:
                is_needed, confidence = await app.analyze_query_for_rag(last_message)
                log(f"RAG 분석 결과:")
                log(f"  - RAG 필요 여부: {is_needed}")
                log(f"  - 신뢰도 점수: {confidence:.2f}")
            continue
            
        elif user_input.lower() == "question":
            log("다음 질문 추천을 생성 중...")
            
            # Option to use RAG for generating questions
            use_rag = False
            if debug_mode:
                rag_choice = input("RAG를 사용하시겠습니까? (y/n): ").lower()
                if rag_choice == 'y':
                    use_rag = True
                log(f"질문 생성에 RAG {('사용' if use_rag else '미사용')}")
                
            questions = await app.get_next_questions(use_rag=use_rag)
            print(f"\n추천 질문:\n{questions}")
            continue
            
        elif user_input.lower() == "recommend":
            log("보험 상품 추천을 생성 중...")
            
            # Option to use RAG for recommendations
            use_rag = True  # 기본값은 True
            if debug_mode:
                rag_choice = input("RAG를 사용하시겠습니까? (y/n): ").lower()
                if rag_choice == 'n':
                    use_rag = False
                log(f"추천 생성에 RAG {('사용' if use_rag else '미사용')}")
                
            recommendation = await app.get_recommendation(use_rag=use_rag)
            print(f"\n추천 상품:\n{recommendation}")
            continue
            
        # Process regular message
        try:
            # Initial RAG analysis
            if debug_mode:
                is_needed, confidence = await app.analyze_query_for_rag(user_input)
                log(f"RAG 분석: 필요={is_needed}, 신뢰도={confidence:.2f}")
            
            log("메시지 처리 중...")
            response_data = await app.process_message(user_input)
            
            # Print detailed debug info if enabled
            if debug_mode:
                log(f"선택된 에이전트: {response_data['agent']}")
                log(f"RAG 사용 여부: {response_data.get('use_rag', False)}")
                
                if response_data.get("handoff_occurred"):
                    log(f"핸드오프: {response_data['previous_agent']} → {response_data['current_agent']}")
                    
                if 'profile_summary' in response_data and response_data['profile_summary']:
                    log("프로필 업데이트 발생")
            
            # Print the response
            print(f"\n{response_data['agent']}: {response_data['response']}")
            
            # If there was a handoff, indicate it
            if response_data.get("handoff_occurred"):
                print(f"(대화가 {response_data['previous_agent']}에서 {response_data['current_agent']}로 전환되었습니다)")
                
        except Exception as e:
            log(f"메시지 처리 중 오류 발생: {str(e)}", "ERROR")
            if debug_mode:
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 