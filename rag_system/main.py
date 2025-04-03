from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from rag_components import RAGSystem, UpstageEmbeddings
import os
import argparse
from dotenv import load_dotenv

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAG 시스템 초기화
rag_system = RAGSystem()

class Document(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}
    id: str = ""

class Query(BaseModel):
    text: str

@app.post("/add_documents")
async def add_documents(documents: List[Document]):
    try:
        rag_system.add_documents([doc.dict() for doc in documents])
        return {"message": "Documents added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query(query: Query):
    try:
        response = rag_system.generate_response(query.text)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    parser = argparse.ArgumentParser(description='RAG 시스템 관리')
    parser.add_argument('--action', type=str, default='preprocess', 
                        choices=['preprocess', 'query', 'test', 'test_embedding'],
                        help='실행할 작업 (preprocess, query, test, test_embedding)')
    parser.add_argument('--query', type=str, 
                        help='RAG 시스템에 질의할 쿼리 (action=query일 경우 필요)')
    parser.add_argument('--data_dir', type=str, default='./data',
                        help='데이터 디렉토리 경로')
    parser.add_argument('--collection', type=str, default='insurance_docs',
                        help='ChromaDB 컬렉션 이름')
    
    args = parser.parse_args()
    
    if args.action == 'test_embedding':
        test_upstage_embedding()
        return
    
    # RAG 시스템 초기화
    rag_system = RAGSystem(collection_name=args.collection)
    
    if args.action == 'preprocess':
        print(f"데이터 전처리를 시작합니다. 데이터 디렉토리: {args.data_dir}")
        rag_system.preprocess_insurance_documents(data_dir=args.data_dir)
        print("데이터 전처리가 완료되었습니다.")
        
    elif args.action == 'query':
        if not args.query:
            print("질의할 쿼리를 --query 인자로 제공해주세요.")
            return
        
        print(f"질의: {args.query}")
        response = rag_system.generate_response(args.query)
        print(f"응답: {response}")
        
    elif args.action == 'test':
        # 테스트 쿼리 목록
        test_queries = [
            "한화 운전자 보험의 주요 보장 내용은 무엇인가요?",
            "교통사고처리지원금의 보장 한도는 얼마인가요?",
            "운전자 보험에서 면책 기간이 있나요?",
            "한화 다이렉트 3400 운전자보험의 특징은 무엇인가요?",
            "자동차 사고시 벌금 보장 한도는 얼마인가요?"
        ]
        
        print("RAG 시스템 테스트 시작")
        for i, query in enumerate(test_queries, 1):
            print(f"\n테스트 {i}: {query}")
            response = rag_system.generate_response(query)
            print(f"응답: {response}")
            
        print("\nRAG 시스템 테스트 완료")

def test_upstage_embedding():
    """Upstage 임베딩 모델 테스트"""
    print("Upstage 임베딩 모델 테스트 중...")
    
    # 임베딩 모델 초기화
    embeddings = UpstageEmbeddings(
        api_key="up_e7ZFHyEsiJPR63d4FLV1aHTBZiE5w",
        model="embedding-query"
    )
    
    # 테스트 문장
    test_texts = [
        "한화 운전자 보험의 주요 보장 내용",
        "교통사고처리지원금의 보장 한도",
        "운전자 보험의 면책 기간"
    ]
    
    # 임베딩 생성 및 출력
    for i, text in enumerate(test_texts, 1):
        try:
            embedding = embeddings.embed_query(text)
            vector_dim = len(embedding)
            print(f"\n[{i}] 텍스트: '{text}'")
            print(f"임베딩 차원: {vector_dim}")
            print(f"임베딩 벡터 (처음 5개 요소): {embedding[:5]}")
        except Exception as e:
            print(f"오류 발생: {str(e)}")
    
    print("\nUpstage 임베딩 모델 테스트 완료")

if __name__ == "__main__":
    main() 