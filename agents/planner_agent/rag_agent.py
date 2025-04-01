from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from langchain.llms import OpenAI
from langchain.chains import LLMChain

load_dotenv()

mongodb_uri=os.getenv("MONGODB_URI")
mongodb_db=os.getenv("MONGODB_DB")
openai_api_key = os.getenv("OPENAI_API_KEY")
from agents.planner_agent.base_agent import BaseAgent


class RAGAgent(BaseAgent):
    def __init__(self):
        self.mongodb_uri = mongodb_uri
        self.mongodb_db = mongodb_db
        self.mongodb_collection = 'insurance_docs'

        self.vectorstore = self._connect_vectorstore()
        self.qa_chain = self._create_qa_chain()

        super().__init__(
            name="RAGAssistant",
            system_message="당신은 문서 기반 질문에 답변하는 RAG 에이전트입니다."
        )

        self.agent.llm_config = {"functions": [self.qa_chain.run]}

    def _connect_vectorstore(self):
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
        llm = OpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key)
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )