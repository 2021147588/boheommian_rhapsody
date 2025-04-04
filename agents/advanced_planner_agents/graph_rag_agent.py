import os
import json
import requests
from openai import OpenAI
from agents.advanced_planner_agents.advanced_base_agent import AdvancedBaseAgent
from dotenv import load_dotenv
from agents.advanced_planner_agents.sales_agent import AdvancedSalesAgent

load_dotenv()

class GraphRAGAgent(AdvancedBaseAgent):
    def __init__(self):
        # GraphDB API 엔드포인트 설정
        self.url = os.environ.get("GRAPH_DB_URI")
        if self.url is None:
            raise ValueError(f"No graph db uri in .env.")
        
        # OpenAI 클라이언트 초기화 (LLM 호출용)
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 상위 클래스 초기화
        super().__init__(
            name="Graph RAG Agent",
            system_message=(
                "당신은 **지식 그래프 기반 정보 검색 전문가**입니다.\n"
                "주요 임무는 사용자의 질문에 대해 **지식 그래프 데이터베이스를 검색**하여 정확하고 사실적인 정보를 제공하는 것입니다.\n"
                "**반드시 다음 지침을 따르세요:**\n"
                "1. 사용자가 **개념, 관계, 사실 정보 등**에 대해 질문하면, **반드시 `search_graph` 도구를 사용**하여 그래프 데이터베이스에서 관련 정보를 검색하고 답변해야 합니다.\n"
                "2. `search_graph` 도구 사용 시, 검색된 정보를 바탕으로 질문에 직접적으로 답변해야 합니다.\n"
                "3. **`transfer_to_sales_agent` 도구는 다음 경우에만 제한적으로 사용해야 합니다:**\n"
                "    a) `search_graph`로 정보를 찾았으나, 사용자가 **추가적인 영업 상담, 개인 맞춤 견적, 가입 절차 안내** 등을 명시적으로 요청할 때.\n"
                "    b) 검색된 정보만으로는 답변이 불충분하고, 질문 내용이 그래프 검색 범위를 벗어나는 복잡한 상담이라고 판단될 때.\n"
                "    c) 사용자가 명확하게 '영업 담당자와 연결해달라', '가입 상담 받고 싶다' 등 전환을 요청할 때.\n"
                "4. **절대로 단순 정보 검색 요청에 `transfer_to_sales_agent` 도구를 사용하지 마세요.** 이 경우에는 `search_graph`를 사용해야 합니다.\n"
                "5. 사용자의 질문 의도를 명확히 파악하고, 정보 검색이 필요한 질문인지, 영업 상담이 필요한 질문인지 정확하게 판단하여 적절한 도구를 사용하세요."
            ),
            model="gpt-4o-mini",
            tools=[
                self.search_graph,
                self.transfer_to_sales_agent
            ]
        )
    
    def retrieve_relevant_info(self, query: str, mode: str = "hybrid"):
        """쿼리와 관련된 정보를 GraphDB에서 검색"""
        try:
            print(f"[Graph RAG] Querying GraphDB with: '{query}' to '{self.url}' in mode: '{mode}'")
           
            payload = {
            "query": f"{query}",
            "mode": "hybrid",
        }
            
            response = requests.post(self.url, json=payload)
            response.raise_for_status()  # 오류 발생 시 예외 처리
            
            if response.status_code == 200:
                result = response.json()['response']
                print(f"[Graph RAG] GraphDB query successful, response: {response}")
                return result
            else:
                print(f"[Graph RAG ERROR] GraphDB query failed with status code: {response.status_code}")
                return {"error": f"GraphDB query failed with status code: {response.status_code}"}
                
        except Exception as e:
            print(f"[Graph RAG ERROR] Error querying GraphDB: {e}")
            return {"error": f"Error querying GraphDB: {str(e)}"}
    
    def search_graph(self, query: str, mode: str = "/hybrid"):
        """
        **[핵심 정보 검색 도구] 사용자가 개념, 관계, 사실 정보 등에 대해 질문할 때 사용합니다.**
        이 도구는 GraphDB에서 관련 정보를 검색하고, 그 내용을 바탕으로 답변을 생성합니다.
        예: '피타고라스의 정리는 무엇인가요?', '인공지능과 머신러닝의 차이점은?', '양자 컴퓨팅이란 무엇인가요?'
        """
        # 도구 호출 시 명확한 로그 추가
        print(f"\n--- [Graph RAG Agent Tool Execution Start: search_graph] ---")
        print(f"Query received: {query}")
        print(f"Mode: {mode}")
        
        try:
            # GraphDB에 쿼리 보내기
            graph_result = self.retrieve_relevant_info(query, mode)
            
            if "error" in graph_result:
                print(f"[Graph RAG ERROR] {graph_result['error']}")
                return f"정보 검색 중 오류가 발생했습니다: {graph_result['error']}"
            
            # 검색 결과가 없는 경우
            if not graph_result or (isinstance(graph_result, dict) and not graph_result.get("results")):
                print("[Graph RAG] No relevant information found in the graph database.")
                return "죄송합니다, 요청하신 내용과 정확히 일치하는 정보를 그래프 데이터베이스에서 찾지 못했습니다. 다른 질문이나 도움이 필요하시면 말씀해주세요."
            
            # 검색 결과를 문자열로 변환
            context = json.dumps(graph_result, ensure_ascii=False, indent=2)
            
            # LLM을 사용하여 답변 생성
            prompt = f"""다음은 사용자의 질문과 관련된 지식 그래프 데이터베이스의 검색 결과입니다. 이 정보를 바탕으로 사용자의 질문에 간결하고 명확하게 답변해주세요. 검색 결과만으로 답변할 수 없는 추측이나 개인적인 의견은 배제하고, 오직 제공된 컨텍스트에 기반하여 답변해야 합니다. 만약 컨텍스트에 질문과 직접 관련된 내용이 없다면, "관련 정보를 찾을 수 없습니다." 라고 답변해주세요.

[그래프 데이터베이스 검색 결과]
{context}

[사용자 질문]
{query}

[답변]"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3  # 더 사실 기반 답변을 위해 온도 낮춤
            )
            
            final_response = response.choices[0].message.content
            print(f"Response generated: {final_response}")
            print(f"--- [Graph RAG Agent Tool Execution End: search_graph] ---\n")
            return final_response
            
        except Exception as e:
            print(f"[ERROR] search_graph 실행 중 오류: {e}")
            print(f"--- [Graph RAG Agent Tool Execution End: search_graph (Error)] ---\n")
            return f"정보 검색 중 오류가 발생했습니다: {str(e)}"
    
    def transfer_to_sales_agent(self):
        """
        **[영업 상담 전환 도구] 사용자가 명시적으로 영업 상담, 개인 맞춤 보험료 견적, 가입 절차 안내 등을 요청하거나, 정보 검색만으로는 해결할 수 없는 복잡한 상담이 필요할 때 '제한적으로' 사용합니다.**
        예: '보험 가입 상담 받고 싶어요', '제 상황에 맞는 보험료 알려주세요', '가입하려면 어떻게 해야 하나요?', '더 자세한 상담을 원해요.'
        **주의: 단순 정보 질문에는 절대 사용하지 마세요! (search_graph 사용)**
        """
        # 도구 호출 시 명확한 로그 추가
        print(f"\n--- [Graph RAG Agent Tool Execution Start: transfer_to_sales_agent] ---")
        print("Reason: Transferring to sales agent based on user request or complexity.")
        
        # 실제 반환은 에이전트 객체 (Orchestrator가 처리)
        sales_agent_instance = AdvancedSalesAgent()
        
        print(f"--- [Graph RAG Agent Tool Execution End: transfer_to_sales_agent] ---\n")
        return sales_agent_instance
