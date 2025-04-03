import os
import json
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from autogen import Agent, AssistantAgent, UserProxyAgent
from dotenv import load_dotenv
from openai import OpenAI
import re

load_dotenv()

class UpstageEmbeddings:
    """Upstage API를 사용한 임베딩 생성 클래스"""
    
    def __init__(self, api_key=None, model="embedding-query"):
        self.api_key = api_key or os.environ.get("UPSTAGE_API_KEY") or "up_e7ZFHyEsiJPR63d4FLV1aHTBZiE5w"
        self.model = model
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.upstage.ai/v1"
        )
        
    def embed_query(self, text):
        """텍스트에 대한 임베딩 벡터 생성"""
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        
        return response.data[0].embedding
    
    def embed_documents(self, documents):
        """문서 목록에 대한 임베딩 벡터 생성"""
        return [self.embed_query(doc) for doc in documents]

class RAGSystem:
    def __init__(self, collection_name: str = "insurance_docs"):
        self.collection_name = collection_name
        self.embedding_model = UpstageEmbeddings(
            api_key="up_e7ZFHyEsiJPR63d4FLV1aHTBZiE5w",
            model="embedding-query"
        )
        
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(path="./rag_system/data")
        
        # 기존 컬렉션이 있다면 재사용, 없으면 생성
        try:
            self.collection = self.client.get_collection(self.collection_name)
            print(f"Using existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name
            )
            print(f"Created new collection: {self.collection_name}")
        
        # AutoGen 에이전트 초기화
        self.rag_agent = AssistantAgent(
            name="RAG_Agent",
            system_message="""You are an insurance expert that uses RAG (Retrieval Augmented Generation) 
            to provide accurate and personalized insurance consultation. Your responses should be based on 
            the retrieved information and maintain a professional, empathetic tone.""",
            llm_config={
                "config_list": [{
                    "model": "gpt-4o-mini",
                    "api_key": os.environ.get("OPENAI_API_KEY")
                }],
                "temperature": 0.7
            }
        )
        
        self.user_proxy = UserProxyAgent(
            name="User_Proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
            llm_config=False
        )
    
    def preprocess_insurance_documents(self, data_dir: str = "./data"):
        """
        데이터 디렉토리에서 보험 문서를 읽고 청크로 분할하여 벡터 DB에 저장
        
        Args:
            data_dir: 보험 데이터가 있는 디렉토리 경로
        """
        print(f"Preprocessing documents from {data_dir}")
        # 이미 벡터 DB에 문서가 있는지 확인
        collection_count = len(self.collection.get()["ids"])
        if collection_count > 0:
            print(f"Collection already contains {collection_count} documents. Skipping preprocessing.")
            return
        
        # 데이터 디렉토리에서 JSON 파일 목록 가져오기
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        
        # 각 JSON 파일 처리
        documents = []
        doc_id = 1
        
        for file in json_files:
            file_path = os.path.join(data_dir, file)
            print(f"Processing file: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if data.get("success") and data.get("content") and data.get("content").get("text"):
                        # 텍스트 콘텐츠 추출
                        text = data["content"]["text"]
                        
                        # 문서를 청크로 분할
                        chunks = self._chunk_text(text)
                        
                        for i, chunk in enumerate(chunks):
                            # 의미 있는 텍스트만 필터링 (너무 짧거나 의미 없는 텍스트 제외)
                            if len(chunk.strip()) < 50 or not any(char.isalpha() for char in chunk):
                                continue
                            
                            documents.append({
                                "id": f"doc_{doc_id}_{i}",
                                "content": chunk,
                                "metadata": {
                                    "source": file,
                                    "chunk_id": i
                                }
                            })
                            
                            # 100개 문서마다 벡터 DB에 추가
                            if len(documents) >= 100:
                                self.add_documents(documents)
                                print(f"Added {len(documents)} documents to vector DB")
                                documents = []
            except json.JSONDecodeError:
                print(f"Error: Could not parse JSON in {file_path}, skipping file.")
                continue
            
            doc_id += 1
        
        # 남은 문서 추가
        if documents:
            self.add_documents(documents)
            print(f"Added final {len(documents)} documents to vector DB")
        
        print(f"Total documents in collection: {len(self.collection.get()['ids'])}")
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        텍스트를 오버랩되는 청크로 분할
        
        Args:
            text: 분할할 텍스트
            chunk_size: 각 청크의 최대 크기
            overlap: 인접 청크 간 오버랩 크기
        
        Returns:
            List[str]: 청크 목록
        """
        # 개행을 기준으로 텍스트 분할하여 단락 생성
        paragraphs = text.split('\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n"
            else:
                # 청크가 이미 있으면 추가하고 새 청크 시작
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # 단락이 최대 크기보다 크면, 단어 단위로 분할
                if len(para) > chunk_size:
                    words = para.split()
                    current_chunk = ""
                    for word in words:
                        if len(current_chunk) + len(word) + 1 <= chunk_size:
                            current_chunk += word + " "
                        else:
                            chunks.append(current_chunk.strip())
                            # 오버랩을 위해 이전 청크의 일부를 새 청크에 추가
                            current_words = current_chunk.split()
                            overlap_words = current_words[-min(len(current_words), overlap//5):]
                            current_chunk = " ".join(overlap_words) + " " + word + " "
                else:
                    # 오버랩을 위해 이전 청크의 마지막 부분 가져오기
                    if chunks and overlap > 0:
                        last_chunk = chunks[-1]
                        overlap_content = last_chunk[-min(len(last_chunk), overlap):]
                        current_chunk = overlap_content + "\n" + para + "\n"
                    else:
                        current_chunk = para + "\n"
        
        # 마지막 청크 추가
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """문서를 벡터 데이터베이스에 추가"""
        if not documents:
            return
            
        ids = []
        docs = []
        metadatas = []
        embeddings = []
        
        for doc in documents:
            # 문서 임베딩 생성 - OpenAI 임베딩 모델 사용
            embedding = self.embedding_model.embed_query(doc["content"])
            
            ids.append(doc.get("id", str(len(self.collection.get()["ids"]) + 1)))
            docs.append(doc["content"])
            metadatas.append(doc.get("metadata", {}))
            embeddings.append(embedding)
        
        # ChromaDB에 문서 추가
        self.collection.add(
            embeddings=embeddings,
            documents=docs,
            metadatas=metadatas,
            ids=ids
        )
    
    def retrieve_relevant_docs(self, query: str, n_results: int = 5) -> List[str]:
        """쿼리와 관련된 문서 검색"""
        # 쿼리 임베딩 생성
        query_embedding = self.embedding_model.embed_query(query)
        
        # 관련 문서 검색
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results["documents"][0]
    
    def generate_response(self, query: str) -> str:
        """RAG를 사용하여 응답 생성"""
        # 관련 문서 검색
        relevant_docs = self.retrieve_relevant_docs(query)
        
        # 컨텍스트 구성
        context = "\n".join(relevant_docs)
        
        # 프롬프트 구성
        prompt = f"""다음 컨텍스트를 바탕으로 질문에 답변해주세요.
        질문과 관련된 정보가 컨텍스트에 없다면 그렇게 말씀해주세요.
        
        컨텍스트:
        {context}
        
        질문: {query}
        
        답변:"""
        
        # AutoGen을 사용하여 응답 생성
        self.user_proxy.initiate_chat(
            self.rag_agent,
            message=prompt,
            max_turns=1
        )
        
        # 마지막 메시지에서 응답 추출
        response = self.rag_agent.last_message()["content"]
        return response

def is_rag_needed(query: str) -> bool:
    """
    쿼리가 RAG가 필요한 질문인지 확인
    
    Args:
        query: 사용자 쿼리
        
    Returns:
        bool: RAG가 필요하면 True, 아니면 False
    """
    # 보험 관련 키워드 정의
    insurance_keywords = [
        '보험', '약관', '보장', '보상', '특약', '면책', '만기', '환급금', '갱신', '갱신형',
        '보험료', '가입', '보험금', '청구', '지급', '한도', '한화', '운전자', '자기부담금',
        '상해', '질병', '입원', '통원', '수술', '진단', '치료', '실비', '보장범위', '암',
        '골절', '진단비', '벌금', '교통사고', '자동차', '운전', '면허', '대중교통', '상해보험'
    ]
    
    # 보험 상품 설명이나 조건에 관한 질문 패턴
    explanation_patterns = [
        r'(무엇|뭐|어떤|어떻게|왜|언제|얼마나|몇|어디|누구).*\?',
        r'설명해',
        r'알려줘',
        r'가르쳐',
        r'차이점',
        r'비교',
        r'보장.*내용',
        r'보험.*종류',
        r'약관.*내용',
        r'보험.*특징',
        r'[0-9]+%',
        r'[0-9]+원',
        r'한도',
        r'기간',
        r'조건'
    ]
    
    # 쿼리에 보험 관련 키워드가 있는지 확인
    has_keyword = any(keyword in query for keyword in insurance_keywords)
    
    # 쿼리가 설명이나 정보 요청 패턴과 일치하는지 확인
    is_explanation = any(re.search(pattern, query) for pattern in explanation_patterns)
    
    return has_keyword and is_explanation 