import requests

# 접속하려는 LightRAG 서버 주소
url = "http://localhost:8000/query"

# 보낼 질문과 모드 설정
query_text = "보험료 납입 기간이 끝나면 어떻게 되나요? 약관 확인인"
query_mode = "hybrid"  # 사용할 모드 (hybrid, mix, local, global, naive 등)

payload = {
    "query": query_text,
    "mode": query_mode
}
headers = {
    "Content-Type": "application/json"
}

print(f"Sending request to {url} with payload: {payload}")

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # 오류 발생 시 예외 처리

    print("응답 내용:")
    print(response.json())

except requests.exceptions.RequestException as e:
    print(f"Error during request: {e}")
    # 서버가 실행 중이지 않거나, 주소가 잘못되었거나, 요청 형식이 잘못되었을 수 있습니다.
except Exception as e:
    print(f"An unexpected error occurred: {e}")
