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
        print("[DEBUG] Initializing GraphRAGAgent")
        # GraphDB API 엔드포인트 설정
        self.url = os.environ.get("GRAPH_DB_URI")
        print(f"[DEBUG] GraphDB URI: {self.url}")
        if self.url is None:
            print("[DEBUG ERROR] No graph db uri found in .env")
            raise ValueError(f"No graph db uri in .env.")
        
        # OpenAI 클라이언트 초기화 (LLM 호출용)
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("[DEBUG] OpenAI client initialized")

        # 상위 클래스 초기화
        print("[DEBUG] Initializing parent class with tools and system message")
        super().__init__(
            name="Graph RAG Agent",
            system_message=(
                "당신은 **지식 그래프 기반 정보 검색 전문가**입니다.\n"
                "주요 임무는 사용자의 질문에 대해 **지식 그래프 데이터베이스를 검색**하여 정확하고 사실적인 정보를 제공하는 것입니다.\n"
                "**반드시 다음 순서로 처리하세요:**\n"
                "1. 사용자의 모든 질문에 대해 **항상 먼저 `search_graph` 도구를 사용**하여 그래프 데이터베이스에서 정보를 검색하세요.\n"
                "2. **검색 결과가 있는 경우에만** 그 정보를 바탕으로 직접 답변하세요.\n"
                "3. **`retrieve_relevant_info` 도구는 LLM 처리 없이 원시 데이터가 필요한 경우에만 사용하세요.**\n"
                "4. **에이전트 전환이 필요한 경우에만** `transfer_to_sales_agent` 도구를 사용하세요. 다음과 같은 경우에만 사용하세요:\n"
                "   a) 사용자가 명시적으로 '영업 담당자와 연결해달라', '가입 상담 받고 싶다'고 요청한 경우\n"
                "   b) 사용자가 개인 맞춤 견적이나 가입 절차에 대한 상세 설명을 요구하는 경우\n"
                "   c) `search_graph`로 충분한 정보를 찾지 못했으며, 질문이 영업 상담이 필요한 성격인 경우\n"
                "5. **절대로 텍스트 응답에 'HANDOFF_TO_' 같은 마커를 포함하지 마세요.** 전환이 필요한 경우 오직 `transfer_to_sales_agent` 함수를 호출하여 직접 에이전트 객체를 반환하세요.\n"
                "6. 모든 일반적인 정보 요청에는 `search_graph`만 사용하세요. 정보를 찾을 수 없는 경우에도 바로 영업 에이전트로 전환하지 말고, 다른 방식으로 질문해 보라고 안내하세요."
            ),
            model="gpt-4o-mini",
            tools=[
                self.search_graph,
                self.transfer_to_sales_agent,
                self.retrieve_relevant_info
            ]
        )
        print("[DEBUG] GraphRAGAgent initialization complete")
    
    def process_message(self, message):
        """Override the process_message method to force search_graph first"""
        print(f"[DEBUG] GraphRAGAgent processing message: {message}")
        
        # Check for sales-specific keywords that might indicate direct sales agent need
        sales_keywords = [
            "가입하고 싶어요", "가입 절차", "가입 상담", "견적 문의", "보험료 확인", 
            "가입 신청", "영업사원", "상담원", "연결해 주세요", "직접 상담"
        ]
        
        # If explicitly asking for sales consultation, allow direct transfer
        is_direct_sales_request = any(keyword in message for keyword in sales_keywords)
        
        if is_direct_sales_request:
            print(f"[DEBUG] Direct sales request detected, allowing standard processing")
            result = super().process_message(message)
        else:
            # For all other queries, force using search_graph first
            print(f"[DEBUG] Information query detected, forcing search_graph usage")
            try:
                # Force using search_graph
                search_result = self.search_graph(query=message)
                print(f"[DEBUG] Forced search_graph completed")
                
                # Return the search result directly
                return search_result
            except Exception as e:
                print(f"[DEBUG] Error in forced search_graph: {str(e)}")
                # Fall back to standard processing if search fails
                result = super().process_message(message)
        
        print(f"[DEBUG] GraphRAGAgent process_message result: {result}")
        return result
    
    def retrieve_relevant_info(self, query: str, mode: str = "hybrid"):
        """쿼리와 관련된 정보를 GraphDB에서 검색"""
        print(f"[DEBUG] retrieve_relevant_info called with query: '{query}', mode: '{mode}'")
        try:
            print(f"[Graph RAG] Querying GraphDB with: '{query}' to '{self.url}' in mode: '{mode}'")
           
            payload = {
            "query": f"{query}",
            "mode": "hybrid",
            }
            print(f"[DEBUG] Payload prepared: {payload}")
            
            print(f"[DEBUG] Sending POST request to {self.url}")
            response = requests.post(self.url, json=payload)
            print(f"[DEBUG] Response status code: {response.status_code}")
            response.raise_for_status()  # 오류 발생 시 예외 처리
            
            if response.status_code == 200:
                result = response.json()['response']
                print(f"[DEBUG] Response JSON structure: {list(response.json().keys())}")
                print(f"[Graph RAG] GraphDB query successful, response: {response}")
                print(f"[DEBUG] Returning result of length: {len(str(result))}")
                print(f"[DEBUG] Result preview: {str(result)[:500]}...")  # Show first 500 chars
                return result
            else:
                print(f"[Graph RAG ERROR] GraphDB query failed with status code: {response.status_code}")
                print(f"[DEBUG] Error response content: {response.text}")
                return {"error": f"GraphDB query failed with status code: {response.status_code}"}
                
        except Exception as e:
            print(f"[Graph RAG ERROR] Error querying GraphDB: {e}")
            print(f"[DEBUG] Exception details: {type(e).__name__}, {str(e)}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            return {"error": f"Error querying GraphDB: {str(e)}"}
    
    def search_graph(self, query: str, mode: str = "/hybrid"):
        """
        **[핵심 정보 검색 도구] 사용자가 개념, 관계, 사실 정보 등에 대해 질문할 때 사용합니다.**
        이 도구는 GraphDB에서 관련 정보를 검색하고, 그 내용을 바탕으로 답변을 생성합니다.
        """
        # 도구 호출 시 명확한 로그 추가
        print(f"\n--- [Graph RAG Agent Tool Execution Start: search_graph] ---")
        print(f"[DEBUG] search_graph called with query: '{query}', mode: '{mode}'")
        print(f"Query received: {query}")
        print(f"Mode: {mode}")
        
        # Fix the mode parameter - it has a "/" prefix which might cause issues
        if mode.startswith("/"):
            mode = mode[1:]
            print(f"[DEBUG] Fixed mode parameter: '{mode}'")
        
        try:
            # GraphDB에 쿼리 보내기
            print(f"[DEBUG] Calling retrieve_relevant_info")
            graph_result = self.retrieve_relevant_info(query, mode)
            print(f"[DEBUG] retrieve_relevant_info returned result type: {type(graph_result)}")
            
            if "error" in graph_result:
                print(f"[Graph RAG ERROR] {graph_result['error']}")
                print(f"[DEBUG] Error detected in graph_result, returning error message")
                return f"정보 검색 중 오류가 발생했습니다: {graph_result['error']}"
            
            # 검색 결과가 없는 경우
            print(f"[DEBUG] Checking if result is empty")
            if not graph_result:
                print("[Graph RAG] No relevant information found in the graph database.")
                print(f"[DEBUG] No results found, returning empty result message")
                return "죄송합니다, 요청하신 내용과 정확히 일치하는 정보를 그래프 데이터베이스에서 찾지 못했습니다. 다른 질문이나 도움이 필요하시면 말씀해주세요."
            
            # 검색 결과 구조 체크를 더 엄격하게 수정
            is_empty = False
            if isinstance(graph_result, dict):
                print(f"[DEBUG] Result keys: {list(graph_result.keys())}")
                # Check various possible empty result structures
                if not graph_result.get("results") and not graph_result.get("data") and not graph_result.get("content"):
                    is_empty = True
            
            if is_empty:
                print("[Graph RAG] Empty dictionary result from graph database.")
                return "죄송합니다, 요청하신 내용과 관련된 정보를 그래프 데이터베이스에서 찾지 못했습니다. 다른 질문이나 도움이 필요하시면 말씀해주세요."
            
            # 검색 결과를 문자열로 변환
            print(f"[DEBUG] Converting graph_result to JSON string")
            context = json.dumps(graph_result, ensure_ascii=False, indent=2)
            print(f"[DEBUG] Context JSON created, length: {len(context)}")
            
            # LLM을 사용하여 답변 생성
            print(f"[DEBUG] Preparing prompt for LLM")
            prompt = f"""다음은 사용자의 질문과 관련된 지식 그래프 데이터베이스의 검색 결과입니다. 이 정보를 바탕으로 사용자의 질문에 간결하고 명확하게 답변해주세요. 검색 결과만으로 답변할 수 없는 추측이나 개인적인 의견은 배제하고, 오직 제공된 컨텍스트에 기반하여 답변해야 합니다. 만약 컨텍스트에 질문과 직접 관련된 내용이 없다면, "관련 정보를 찾을 수 없습니다." 라고 답변해주세요.

[그래프 데이터베이스 검색 결과]
{context}

[사용자 질문]
{query}

[답변]"""

            print(f"[DEBUG] Calling OpenAI API with model: gpt-4o-mini")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3  # 더 사실 기반 답변을 위해 온도 낮춤
            )
            
            print(f"[DEBUG] OpenAI API response received")
            final_response = response.choices[0].message.content
            print(f"[DEBUG] Generated response length: {len(final_response)}")
            print(f"Response generated: {final_response}")
            print(f"--- [Graph RAG Agent Tool Execution End: search_graph] ---\n")
            return final_response
            
        except Exception as e:
            print(f"[ERROR] search_graph 실행 중 오류: {e}")
            print(f"[DEBUG] Exception in search_graph: {type(e).__name__}, {str(e)}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
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
        print(f"[DEBUG] transfer_to_sales_agent called")
        print("Reason: Transferring to sales agent based on user request or complexity.")
        
        # 실제 반환은 에이전트 객체 (Orchestrator가 처리)
        print(f"[DEBUG] Creating sales agent instance")
        sales_agent_instance = AdvancedSalesAgent()
        print(f"[DEBUG] Sales agent instance created: {type(sales_agent_instance)}")
        
        print(f"--- [Graph RAG Agent Tool Execution End: transfer_to_sales_agent] ---\n")
        return sales_agent_instance
