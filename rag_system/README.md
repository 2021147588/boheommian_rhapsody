# 보험 상담 RAG 시스템

이 프로젝트는 보험 상담을 위한 RAG(Retrieval Augmented Generation) 시스템을 구현하고 에이전트 아키텍처와 통합한 코드를 제공합니다.

## 개요

이 RAG 시스템은 보험 약관 문서를 자동으로 처리하고 벡터화하여 사용자의 질문에 정확한 정보를 제공합니다. 시스템은 다음 구성 요소를 포함합니다:

1. **문서 전처리**: 보험 약관 JSON 파일에서 텍스트를 추출하고 청크로 분할
2. **벡터 저장소**: ChromaDB를 이용한 임베딩 저장 및 검색 
3. **쿼리 분류기**: 사용자 쿼리가 RAG가 필요한지 판단
4. **에이전트 통합**: Router와 Sales 에이전트에 RAG 기능 통합

## 기술 스택

- **벡터 DB**: ChromaDB
- **임베딩 모델**: OpenAI Embeddings
- **LLM**: OpenAI GPT 모델 (gpt-4o-mini, gpt-3.5-turbo)
- **프레임워크**: Python, AutoGen

## 디렉토리 구조

```
rag-system/
  ├── data/                # 벡터 DB 저장 디렉토리
  ├── rag_components.py    # RAG 핵심 구성 요소
  ├── main.py              # 메인 실행 파일
  └── requirements.txt     # 필요한 라이브러리
  
data/                      # 보험 약관 데이터
  ├── LA02762001_part1.json
  ├── LA02762001_part2.json
  └── ...

agents/
  ├── advanced_agents/
  │   ├── router_agent.py  # 쿼리 라우팅 에이전트
  │   ├── rag_agent.py     # RAG 전용 에이전트
  │   └── sales_agent.py   # 영업 에이전트 (RAG 통합)
  └── advanced_orchestrator.py  # 에이전트 오케스트레이터
```

## 주요 기능

### 1. 문서 전처리 및 인덱싱

```python
# 데이터 전처리 실행
python rag-system/main.py --action preprocess --data_dir ./data
```

JSON 파일에서 텍스트를 추출하고 청크로 분할하여 ChromaDB에 저장합니다. 중복 인덱싱을 방지하기 위해 이미 인덱싱된 경우 건너뜁니다.

### 2. 쿼리 분류

`is_rag_needed()` 함수는 사용자 쿼리를 분석하여 RAG가 필요한 질문인지 판단합니다:

- 보험 관련 키워드 포함 여부 확인
- 설명이나 정보 요청 패턴 일치 확인

### 3. 에이전트 라우팅

`AdvancedRouterAgent`는 사용자 질문을 분석하여 적절한 에이전트로 라우팅:

- 보험 상품 정보 질문 → RAG 에이전트
- 보험 상담 및 추천 질문 → 영업 에이전트

### 4. 영업 에이전트 RAG 통합

영업 에이전트는 두 가지 방식으로 RAG를 활용:

1. `answer_with_rag()`: 영업 에이전트가 직접 RAG 시스템을 사용하여 정보 제공
2. `transfer_to_rag_agent()`: 복잡한 질문은 RAG 전문 에이전트로 전환

## 사용 방법

### 테스트 실행

테스트 스크립트를 실행하여 전체 시스템 검증:

```python
python test_rag_integration.py
```

### 대화 인터페이스 실행

```python
python agents/advanced_orchestrator.py
```

## 확장 방향

1. 추가 보험 문서 인덱싱
2. 임베딩 모델 및 벡터 DB 최적화
3. 다국어 지원 추가
4. 웹 인터페이스 연동 