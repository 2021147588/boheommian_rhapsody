import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from autogen import Agent, AssistantAgent, UserProxyAgent
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

class RAGSystem:
    def __init__(self, collection_name: str = "insurance_docs"):
        self.collection_name = collection_name
        self.embedding_model = OpenAIEmbeddings(
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(path="./data")
        
        # 기존 컬렉션이 있다면 삭제
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        
        # 컬렉션 새로 생성
        self.collection = self.client.create_collection(
            name=self.collection_name
        )
        
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
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """문서를 벡터 데이터베이스에 추가"""
        for doc in documents:
            # 문서 임베딩 생성
            embedding = self.embedding_model.embed_query(doc["content"])
            
            # ChromaDB에 문서 추가
            self.collection.add(
                embeddings=[embedding],
                documents=[doc["content"]],
                metadatas=[doc.get("metadata", {})],
                ids=[doc.get("id", str(len(self.collection.get()["ids"]) + 1))]
            )
    
    def retrieve_relevant_docs(self, query: str, n_results: int = 3) -> List[str]:
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
        prompt = f"""Based on the following context, please answer the question. 
        If the context doesn't contain relevant information, say so.
        
        Context:
        {context}
        
        Question: {query}
        
        Answer:"""
        
        # AutoGen을 사용하여 응답 생성
        self.user_proxy.initiate_chat(
            self.rag_agent,
            message=prompt,
            max_turns=1
        )
        
        # 마지막 메시지에서 응답 추출
        response = self.rag_agent.last_message()["content"]
        return response 