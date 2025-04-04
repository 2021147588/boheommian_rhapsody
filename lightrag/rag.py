import requests

url = "http://localhost:9621/query"

payload = {
    "query": "/mix 한화손해보험 보험료는 어떻게 계산되나요?",
    "mode": "mix"
}

response = requests.post(url, json=payload)

print("응답 내용:")
print(response.json())
