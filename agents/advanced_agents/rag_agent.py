import os
import json
import chromadb
# from chromadb.config import Settings # Settings 는 사용되지 않으므로 제거 가능
from openai import OpenAI
from agents.planner_agent.advanced_base_agent import AdvancedBaseAgent
from dotenv import load_dotenv
from agents.advanced_agents.sales_agent import AdvancedSalesAgent

load_dotenv()

# UpstageEmbeddings 클래스 다시 추가
class UpstageEmbeddings:
    """Upstage API를 사용한 임베딩 생성 클래스"""

    def __init__(self, api_key=None, model="embedding-query"):
        # UPSTAGE_API_KEY 환경 변수 또는 기본값 사용
        self.api_key = api_key or os.environ.get("UPSTAGE_API_KEY")
        if not self.api_key:
             # 환경 변수가 없을 경우 경고 또는 기본 키 사용 (보안상 주의)
             print("[WARN] UPSTAGE_API_KEY environment variable not set. Using default or potentially failing.")
             # self.api_key = "YOUR_DEFAULT_UPSTAGE_KEY_HERE" # 필요시 기본 키 설정
        self.model = model
        # base_url 수정: api.upstage.ai/v1/solar -> api.upstage.ai/v1
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.upstage.ai/v1" # 올바른 Upstage API 엔드포인트
        )
        print(f"[UpstageEmbeddings] Initialized with model: {self.model}")

    def embed_query(self, text):
        """텍스트에 대한 임베딩 벡터 생성"""
        if not self.api_key:
             raise ValueError("Upstage API key is not configured.")
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model,
                # Upstage 모델에 따라 필요한 경우 request_type 추가
                # request_type="embedding-query" # 예시: 모델이 타입을 요구하는 경우
            )
            print(f"[UpstageEmbeddings] Embedding successful for query (first 10 chars): {text[:10]}...")
            return response.data[0].embedding
        except Exception as e:
            print(f"[ERROR] Upstage embedding failed using model '{self.model}': {e}")
            # 모델 못 찾는 오류 시 힌트 제공
            if "model_not_found" in str(e):
                 print(f"[ERROR HINT] Model '{self.model}' not found or deprecated. Check available models at Upstage documentation.")
            raise # 오류를 다시 발생시켜 호출한 곳에서 처리하도록 함

    def embed_documents(self, documents):
        """문서 목록에 대한 임베딩 벡터 생성"""
        embeddings = []
        for doc in documents:
             # 문서 임베딩 시 모델 변경이 필요하면 여기서 처리
             # 예: self.model = "embedding-document"
             embeddings.append(self.embed_query(doc))
        return embeddings


class AdvancedRAGAgent(AdvancedBaseAgent):
    def __init__(self):
        # ChromaDB 설정
        self.collection_name = "insurance_docs_v2"
        self.db_path = "./vector_db"

        # Upstage 임베딩 모델 인스턴스 생성
        try:
            self.embedding_model = UpstageEmbeddings(
                api_key=os.environ.get("UPSTAGE_API_KEY"), # 환경 변수 사용
                model="embedding-query" # 사용할 Upstage 임베딩 모델 지정 (4096 차원)
            )
            print(f"[AdvancedRAGAgent] Initialized Upstage Embeddings with model: {self.embedding_model.model}")
        except Exception as e:
             print(f"[ERROR] Failed to initialize UpstageEmbeddings: {e}")
             self.embedding_model = None # 초기화 실패 시 None 설정

        # OpenAI 클라이언트 초기화 (LLM 호출용)
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # self.openai_embedding_model 속성 제거
        # self.openai_embedding_model = "text-embedding-ada-002"

        # ChromaDB 클라이언트 초기화
        try:
            print(f"[AdvancedRAGAgent] Connecting to ChromaDB at path: {os.path.abspath(self.db_path)}")
            self.client = chromadb.PersistentClient(path=self.db_path)
            try:
                # 변경된 컬렉션 이름으로 가져오기 시도
                self.collection = self.client.get_collection(self.collection_name)
                collection_count = self.collection.count()
                print(f"Using existing collection: '{self.collection_name}' with {collection_count} documents.")
                # 컬렉션 메타데이터 확인하여 모델 일치 여부 검토 (선택적 강화)
                collection_metadata = getattr(self.collection, 'metadata', None)
                if collection_metadata:
                     stored_model = collection_metadata.get('embedding_model')
                     stored_dim = collection_metadata.get('embedding_dimension')
                     print(f"  Collection metadata - Model: {stored_model}, Dimension: {stored_dim}")
                     if stored_model and stored_model != self.embedding_model.model:
                          print(f"[WARN] Collection metadata indicates model '{stored_model}', but agent is using '{self.embedding_model.model}'. Ensure dimensions match or re-ingest data.")
                if collection_count == 0:
                     print(f"[WARN] Collection '{self.collection_name}' exists but is empty. Ensure preprocessing was successful and added documents.")
            except Exception as e:
                 # 컬렉션이 없는 경우 에러 출력 (RAG Agent는 컬렉션을 생성하는 역할이 아님)
                 print(f"[ERROR] Collection '{self.collection_name}' not found in '{self.db_path}'. "
                       f"Please run the preprocessing script (`data_preprocess/preprocess.py`) first to create and populate the collection.")
                 print(f"Underlying error: {e}")
                 self.collection = None # 컬렉션 접근 불가

        except Exception as e:
            print(f"[ERROR] ChromaDB client initialization failed for path '{self.db_path}': {e}")
            self.client = None
            self.collection = None

        # 상위 클래스 초기화
        super().__init__(
            name="RAG Agent",
            system_message=(
                "당신은 **한화손해보험의 보험 문서 기반 정보 검색 전문가**입니다.\n"
                "주요 임무는 사용자의 질문에 대해 **저장된 보험 약관, 상품 설명서, 가이드라인 등의 문서를 검색**하여 정확하고 사실적인 정보를 제공하는 것입니다.\n"
                "**반드시 다음 지침을 따르세요:**\n"
                "1. 사용자가 **보험 상품의 세부 정보, 약관 내용, 보장 범위, 보험료 산정 방식(문서 기반), 용어 정의, 청구 절차 등**에 대해 질문하면, **반드시 `search_documents` 도구를 사용**하여 데이터베이스에서 관련 정보를 검색하고 답변해야 합니다.\n"
                "2. `search_documents` 도구 사용 시, 검색된 문서 내용을 바탕으로 질문에 직접적으로 답변해야 합니다.\n"
                "3. **`transfer_to_sales_agent` 도구는 다음 경우에만 제한적으로 사용해야 합니다:**\n"
                "    a) `search_documents`로 정보를 찾았으나, 사용자가 **추가적인 영업 상담, 개인 맞춤 견적, 가입 절차 안내** 등을 명시적으로 요청할 때.\n"
                "    b) 검색된 정보만으로는 답변이 불충분하고, 질문 내용이 문서 검색 범위를 벗어나는 복잡한 상담(예: 개인 상황에 따른 특수한 경우)이라고 판단될 때.\n"
                "    c) 사용자가 명확하게 '영업 담당자와 연결해달라', '가입 상담 받고 싶다' 등 전환을 요청할 때.\n"
                "4. **절대로 단순 정보 검색 요청(예: '보험료 어떻게 계산돼요?', '이 특약 설명해주세요')에 `transfer_to_sales_agent` 도구를 사용하지 마세요.** 이 경우에는 `search_documents`를 사용해야 합니다.\n"
                "5. 사용자의 질문 의도를 명확히 파악하고, 정보 검색이 필요한 질문인지, 영업 상담이 필요한 질문인지 정확하게 판단하여 적절한 도구를 사용하세요."
            ),
            model="gpt-4o-mini",
            tools=[
                self.search_documents,
                self.transfer_to_sales_agent
            ]
        )
    
    def retrieve_relevant_docs(self, query: str, n_results: int = 5):
        """쿼리와 관련된 문서 검색 (Upstage 임베딩 사용)"""
        if not self.collection:
            print("[RAG DEBUG] Collection not available or not found.")
            return ["검색 기능을 사용할 수 없습니다. 데이터베이스 연결 또는 컬렉션 문제를 확인하세요."]
        if not self.embedding_model:
            print("[RAG ERROR] Embedding model is not initialized.")
            return ["임베딩 모델 초기화 오류로 검색할 수 없습니다."]

        try:
            print(f"[RAG DEBUG] Retrieving documents for query: '{query}' using Upstage model '{self.embedding_model.model}' from collection '{self.collection_name}'")
            query_embedding = self.embedding_model.embed_query(query)
            current_dim = len(query_embedding)
            print(f"[RAG DEBUG] Query embedding dimension: {current_dim}")

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            print(f"[RAG DEBUG] ChromaDB query results: {results}")

            if results and "documents" in results and results["documents"] and results["documents"][0]:
                print(f"[RAG DEBUG] Found {len(results['documents'][0])} documents.")
                return results["documents"][0]
            else:
                print("[RAG DEBUG] No relevant documents found in the collection for this query.")
                return ["관련 문서를 찾을 수 없습니다."]
        except Exception as e:
            print(f"[ERROR] 문서 검색 중 오류: {e}")
            # 차원 불일치 오류 힌트 개선
            if "dimensionality" in str(e):
                 # 컬렉션의 실제 차원 가져오기 시도 (ChromaDB 버전에 따라 다를 수 있음)
                 try:
                      collection_dim = self.collection._embedding_function.dim # 예시, 실제 속성은 다를 수 있음
                 except:
                      collection_dim = "Unknown (check collection metadata or creation script)"
                 print(f"[ERROR HINT] Embedding dimension mismatch!")
                 print(f"  - Agent's current model ('{self.embedding_model.model}') produced dimension: {current_dim if 'current_dim' in locals() else 'Unknown'}")
                 print(f"  - Collection '{self.collection_name}' requires dimension: {collection_dim}")
                 print(f"  - ACTION NEEDED: Ensure 'preprocess.py' uses the *exact same* embedding model ('{self.embedding_model.model}') and re-ingest data after deleting './vector_db'.")
            return [f"검색 중 오류 발생: {str(e)}"]
    
    def search_documents(self, query: str):
        """
        **[핵심 정보 검색 도구] 사용자가 보험 상품의 약관, 보장 내용, 보험료 산정 방식(문서 기반), 용어 정의, 청구 절차 등 문서에 기반한 '사실 정보'를 질문할 때 사용합니다.**
        이 도구는 데이터베이스에서 관련 문서를 검색하고, 그 내용을 바탕으로 답변을 생성합니다.
        예: 'XX보험 표준약관 알려줘', '운전자보험 보장 범위가 어떻게 되나요?', '보험료는 어떤 기준으로 산정되나요?', '자기부담금이란 무엇인가요?'
        """
        # 도구 호출 시 명확한 로그 추가
        print(f"\n--- [RAG Agent Tool Execution Start: search_documents] ---")
        print(f"Query received: {query}")
        try:
            relevant_docs = self.retrieve_relevant_docs(query)
            context = "\n".join(relevant_docs)
            # print(f"[RAG DEBUG] Context created:\n---\n{context}\n---") # 로그 줄임 (필요시 활성화)

            if context == "관련 문서를 찾을 수 없습니다." or not context.strip():
                 print("[RAG DEBUG] No relevant documents found, providing standard response.")
                 final_response = "죄송합니다, 요청하신 내용과 정확히 일치하는 정보를 문서에서 찾지 못했습니다. 다른 질문이나 도움이 필요하시면 말씀해주세요."
            else:
                prompt = f"""다음은 사용자의 질문과 관련된 보험 문서의 일부 내용입니다. 이 정보를 바탕으로 사용자의 질문에 간결하고 명확하게 답변해주세요. 문서 내용만으로 답변할 수 없는 추측이나 개인적인 의견은 배제하고, 오직 제공된 컨텍스트에 기반하여 답변해야 합니다. 만약 컨텍스트에 질문과 직접 관련된 내용이 없다면, "관련 정보를 찾을 수 없습니다." 라고 답변해주세요.

[관련 문서 내용]
{context}

[사용자 질문]
{query}

[답변]"""
                # print(f"[RAG DEBUG] Prompt for LLM:\n---\n{prompt}\n---") # 로그 줄임 (필요시 활성화)

                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3 # 더 사실 기반 답변을 위해 온도 낮춤
                )
                final_response = response.choices[0].message.content
                # print(f"[RAG DEBUG] LLM Response:\n---\n{final_response}\n---") # 로그 줄임

            print(f"Response generated: {final_response}")
            print(f"--- [RAG Agent Tool Execution End: search_documents] ---\n")
            return final_response
        except Exception as e:
            print(f"[ERROR] search_documents 실행 중 오류: {e}")
            print(f"--- [RAG Agent Tool Execution End: search_documents (Error)] ---\n")
            return f"정보 검색 중 오류가 발생했습니다: {str(e)}"
    
    def transfer_to_sales_agent(self):
        """
        **[영업 상담 전환 도구] 사용자가 명시적으로 영업 상담, 개인 맞춤 보험료 견적, 가입 절차 안내 등을 요청하거나, 정보 검색만으로는 해결할 수 없는 복잡한 상담이 필요할 때 '제한적으로' 사용합니다.**
        예: '보험 가입 상담 받고 싶어요', '제 상황에 맞는 보험료 알려주세요', '가입하려면 어떻게 해야 하나요?', '더 자세한 상담을 원해요.'
        **주의: 단순 정보 질문(예: '보험료 어떻게 계산돼요?')에는 절대 사용하지 마세요! (search_documents 사용)**
        """
        # 도구 호출 시 명확한 로그 추가
        print(f"\n--- [RAG Agent Tool Execution Start: transfer_to_sales_agent] ---")
        print("Reason: Transferring to sales agent based on user request or complexity.")
        # 실제 반환은 에이전트 객체 (Orchestrator 가 처리)
        sales_agent_instance = AdvancedSalesAgent()
        print(f"--- [RAG Agent Tool Execution End: transfer_to_sales_agent] ---\n")
        return sales_agent_instance 