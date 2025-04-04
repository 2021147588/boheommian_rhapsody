import os
import json
import openai
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()
# Set OpenAI API key (if not set in environment)
openai.api_key = os.getenv("OPENAI_API_KEY")


# Define the function to call LangChain to analyze conversation
def analyze_conversation(user_info, conversation_log):
    prompt_template = """
    사용자 프로필:
    이름: {user_name}
    나이: {birth_date}
    성별: {gender}
    운전 경험: {driving_experience_years} 년
    사고 이력: {accident_history}
    차량: {vehicle_model} ({vehicle_year})
    보험 설정: {insurance_settings}

    대화 로그: {conversation_log}

    작업: 대화를 분석하여, 상담자가 사용자의 요구에 맞춘 추천을 했는지 평가하세요. 상담자가 사용자를 설득하려는 전략을 사용했는지, 그리고 대화가 실패했다면 그 이유를 설명하세요. 
    또한, 개선할 점을 제안하고, 다음과 같은 항목들을 포함하여 자세한 피드백을 제공하세요:  아래 json 형식을 꼭 지켜주세요, 다른 내용을 절대 출력하지 마세요.
    {{
        "상담자의 전반적인 성과" : ,
        "대화가 실패한 이유" : 실패한 경우에만,
        "개선을 위한 제안" : ,
        "대화의 효과성 및 설득 전략 분석" : ,
        "사용자 만족도 추정" : 
    }}
    """

    # Set the prompt using LangChain's prompt template
    prompt = PromptTemplate.from_template(prompt_template)

    # Initialize LangChain's ChatOpenAI model (using GPT-4)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

    # Create the RunnableSequence with the prompt and the model
    chain = prompt | llm  # Updated to use RunnableSequence

    # Prepare input variables for the prompt
    input_vars = {
        'user_name': user_info['user']['name'],
        'birth_date': user_info['user']['birth_date'],
        'gender': user_info['user']['gender'],
        'driving_experience_years': user_info['user']['driving_experience_years'],
        'accident_history': user_info['user']['accident_history'],
        'vehicle_model': user_info['vehicle']['model'],
        'vehicle_year': user_info['vehicle']['year'],
        'insurance_settings': user_info['insurance_settings'],
        'conversation_log': conversation_log
    }

    # Run the RunnableSequence to get the analysis
    analysis = chain.invoke(input_vars)  # Updated method

    # Access the content of the AIMessage object
    return analysis.content.strip()

# Function to process all files in the provided directory
def process_conversation_logs(json_files_list):
    reports = []
    
    for filename in json_files_list:
        if filename.endswith(".json"):
            filepath = filename
            # Read JSON file
            with open(filepath, 'r', encoding='utf-8') as file:
                log_data = json.load(file)

            # Extract user information and conversation logs
            user_info = log_data['user_info']
            conversation_log = '\n'.join([f"Turn {turn['turn']}: {turn['user_reply']} -> {turn['agent_response']}" for turn in log_data['turns']])

            # Call LangChain to analyze the conversation
            analysis = analyze_conversation(user_info, conversation_log)
            if analysis.startswith("```json"):
                 analysis = analysis[7:-3].strip()  # Remove the first 7 and last 3 characters
            
                    
            # Parse the analysis JSON string into a Python dictionary
            try:
                analysis_data = json.loads(analysis)
                final_report = {
                    "상담자의 전반적인 성과": analysis_data.get("상담자의 전반적인 성과", "N/A"),
                    "대화가 실패한 이유": analysis_data.get("대화가 실패한 이유", "N/A"),
                    "개선을 위한 제안": analysis_data.get("개선을 위한 제안", "N/A"),
                    "대화의 효과성 및 설득 전략 분석": analysis_data.get("대화의 효과성 및 설득 전략 분석", "N/A"),
                    "사용자 만족도 추정": analysis_data.get("사용자 만족도 추정", "N/A"),
                    "conversation_log": conversation_log  # Include full conversation log for reference
                }
                log_data['final_report'] = final_report
                with open(filepath, "w", encoding="utf-8") as updated_file:
                    json.dump(log_data, updated_file, ensure_ascii=False, indent=4)
                    
                reports.append(final_report)
            except json.JSONDecodeError:
                report = {
                    "error": "Failed to parse analysis JSON",
                    "raw_analysis": analysis,
                    "conversation_log": conversation_log
                }
                log_data['final_report'] = report
                with open(filepath, "w", encoding="utf-8") as updated_file:
                    json.dump(log_data, updated_file, ensure_ascii=False, indent=4)
                
                reports.append(report)
    return reports

# Function to generate a final report in JSON format
def generate_report(directory):
    # Ensure the directory exists
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"The directory '{directory}' does not exist.")
    
    # List all JSON files in the directory
    json_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".json")]
    reports = process_conversation_logs(json_files)
    
    # Output the analysis as JSON
    # Optionally, save the report to a file
    final_report = json.dumps(reports, ensure_ascii=False, indent=4)

    return final_report

if __name__ == "__main__":
    # Example usage
    directory_path = os.getenv("RESULT_PATH")

    final_report = generate_report(directory_path)

    # Print the final report
    print(final_report)
    with open(f"{directory_path}_conversation_analysis_report.json", "w", encoding="utf-8") as report_file:
        report_file.write(final_report)
    
