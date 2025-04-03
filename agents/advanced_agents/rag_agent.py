import os
import json
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from agents.planner_agent.advanced_base_agent import AdvancedBaseAgent
from dotenv import load_dotenv

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

class AdvancedRAGAgent(AdvancedBaseAgent):
    def __init__(self):
        # ChromaDB 설정
        self.collection_name = "insurance_docs"
        self.embedding_model = UpstageEmbeddings(
            api_key=os.environ.get("UPSTAGE_API_KEY") or "up_e7ZFHyEsiJPR63d4FLV1aHTBZiE5w",
            model="embedding-query"
        )
        
        # OpenAI 클라이언트 초기화
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # ChromaDB 클라이언트 초기화
        try:
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
        except Exception as e:
            print(f"[ERROR] ChromaDB 설정 중 오류 발생: {e}")
            self.client = None
            self.collection = None
        
        # 상위 클래스 초기화
        super().__init__(
            name="RAG Agent",
            system_message=(
                "당신은 보험 관련 문서 검색을 통해 사용자 질문에 답변하는 전문가입니다. "
                "사용자의 질문에 답변하기 위해 검색 기능을 활용하여 정확한 정보를 제공합니다. "
                "정보가 부족하거나 판매 상담이 필요한 경우 영업 에이전트로 전환합니다."
            ),
            model="gpt-4o-mini",
            tools=[self.search_documents, self.transfer_to_sales_agent]
        )
    
    def retrieve_relevant_docs(self, query: str, n_results: int = 5):
        """쿼리와 관련된 문서 검색"""
        if not self.collection:
            return ["검색 기능을 사용할 수 없습니다. ChromaDB 연결 문제가 발생했습니다."]
        
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.embedding_model.embed_query(query)
            
            # 관련 문서 검색
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # 검색 결과 반환
            if results and "documents" in results and results["documents"]:
                return results["documents"][0]
            else:
                return ["관련 문서를 찾을 수 없습니다."]
        except Exception as e:
            print(f"[ERROR] 문서 검색 중 오류: {e}")
            return [f"검색 중 오류 발생: {str(e)}"]
    
    def search_documents(self, query: str):
        """
        문서를 검색하여 관련 정보를 찾습니다.
        """
        try:
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
            
            # OpenAI API를 사용하여 응답 생성
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"[ERROR] 문서 검색 및 응답 생성 중 오류: {e}")
            return f"검색 및 응답 생성 중 오류 발생: {str(e)}"
    
    def transfer_to_sales_agent(self):
        """
        영업 에이전트로 전환합니다. 제품 추천이나 판매 상담이 필요한 경우 호출합니다.
        """
        from agents.advanced_agents.sales_agent import AdvancedSalesAgent
        return AdvancedSalesAgent() 