from fastapi import FastAPI, UploadFile, File, Form
from app.view import *
import json
import os
import datetime
from agents.conversation import AgentConversation
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agents.generate_analysis import *
load_dotenv()
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_directory = "./static"
app.mount("/static", StaticFiles(directory=static_directory, html=True), name="static")

# Serve the main HTML file
@app.get("/", response_class=HTMLResponse)
async def get_html():
    html_file = Path(f"{static_directory}/index.html")
    if not html_file.exists():
        return HTMLResponse(content="<h1>index.html not found</h1>", status_code=404)
    return FileResponse(html_file)

@app.post("/submit")
async def submit_data(
    file: UploadFile = File(...),
    max_samples: int = Form(10),
    max_turns: int = Form(5)
):
    
        
    file_content = await file.read()
    user_info_list = json.loads(file_content)

    detailed_chat_log = []
    simplified_chat_log = []
    enhanced_chat_log = []  # 새로운 향상된 로그
    success_count = 0
    total_samples = min(len(user_info_list), max_samples)  # 사용자가 지정한 최대 샘플 수만큼만 처리
    
    # results 디렉토리 생성
    results_dir = os.getenv('RESULT_PATH')
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"'{results_dir}' 디렉토리를 생성했습니다.")
    
    # 타임스탬프로 파일명 생성
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file_lists = []
    for i, user_info_dict in enumerate(user_info_list[:total_samples]):
        print(f"\n===== 시뮬레이션 {i+1}/{total_samples} =====")
        user_info = UserInfo(**user_info_dict)
        conversation = AgentConversation(user_info, max_turns=max_turns)  # max_turns 파라미터 추가
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
          
        # 향상된 로그 버전 저장 (enhanced만 저장)
        enhanced_filename = f"{results_dir}/{timestamp}_{user_id}_{user_name}_enhanced.json"
        with open(enhanced_filename, "w", encoding='utf-8') as file:
            json.dump(enhanced_data, file, ensure_ascii=False, indent=4)
            result_file_lists.append(enhanced_filename)
            print(f"향상된 로그를 '{enhanced_filename}' 파일에 저장했습니다.")
    
    final_report = process_conversation_logs(result_file_lists)
    
    
    count = 0
    for item in final_report:
        if item["대화가 실패한 이유"] is None or item["대화가 실패한 이유"] == "N/A":
            count += 1
            
    # 결과 출력
    print(f"\n===== 시뮬레이션 결과 =====")
    print(f"총 샘플: {len(final_report)}")
    print(f"성공 샘플: {count}")
    print(f"성공률: {(count/len(final_report))*100:.1f}%")
    
    # 모든 대화 통합 파일 저장 (향상된 로그 버전만)
    enhanced_all_file = f"{results_dir}/{timestamp}_all_enhanced.json"
    with open(enhanced_all_file, "w", encoding='utf-8') as file:
        result_data = {
            "summary": {
                "total_samples": len(final_report),
                "success_count": {count},
                "success_rate": (count/len(final_report))*100,
                "timestamp": timestamp
            },
            "conversations": enhanced_chat_log,
        }
        # json.dump(result_data, file, ensure_ascii=False, indent=4)
        print(f"모든 향상된 로그를 '{enhanced_all_file}' 파일에 저장했습니다.")

    return {"message": "success", "data": result_data}

if __name__=='__main__':
    uvicorn.run(app="main:app", port=8001, reload=True, host='127.0.0.1')