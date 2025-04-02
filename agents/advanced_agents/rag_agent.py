import os
from dotenv import load_dotenv
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from pymongo import MongoClient
from agents.planner_agent.advanced_base_agent import AdvancedBaseAgent

load_dotenv()

class AdvancedRAGAgent(AdvancedBaseAgent):
    def __init__(self):
        # MongoDB 및 RAG 설정
        self.mongodb_uri = os.getenv("MONGODB_URI")
        self.mongodb_db = os.getenv("MONGODB_DB")
        self.mongodb_collection = 'insurance_docs'
        
        # 벡터 스토어 및 QA 체인 설정
        self.vectorstore = self._connect_vectorstore()
        self.qa_chain = self._create_qa_chain()
        
        # 상위 클래스 초기화
        super().__init__(
            name="RAG Agent",
            system_message=(
                "당신은 보험 관련 문서 검색을 통해 사용자 질문에 답변하는 전문가입니다. "
                "사용자의 질문에 답변하기 위해 검색 기능을 활용하여 정확한 정보를 제공합니다. "
                "정보가 부족하거나 판매 상담이 필요한 경우 영업 에이전트로 전환합니다."
            ),
            model="gpt-3.5-turbo",
            tools=[self.search_documents, self.transfer_to_sales_agent]
        )
    
    def _connect_vectorstore(self):
        """벡터 스토어에 연결합니다."""
        client = MongoClient(self.mongodb_uri)
        db = client[self.mongodb_db]
        collection = db[self.mongodb_collection]
        
        embeddings = OpenAIEmbeddings()
        return MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name="default"
        )
    
    def _create_qa_chain(self):
        """QA 체인을 생성합니다."""
        llm = OpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )
    
    def search_documents(self, query: str):
        """
        문서를 검색하여 관련 정보를 찾습니다.
        """
        try:
            result = self.qa_chain.run(query)
            return f"검색 결과: {result}"
        except Exception as e:
            return f"검색 중 오류 발생: {str(e)}"
    
    def transfer_to_sales_agent(self):
        """
        영업 에이전트로 전환합니다. 제품 추천이나 판매 상담이 필요한 경우 호출합니다.
        """
        from agents.advanced_agents.sales_agent import AdvancedSalesAgent
        return AdvancedSalesAgent() 