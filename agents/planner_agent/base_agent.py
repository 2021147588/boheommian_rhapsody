from autogen import AssistantAgent
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, name: str, system_message: str):
        self.agent = AssistantAgent(
            name=name,
            system_message=system_message,
            code_execution_config={"use_docker": False},
            llm_config={
                "config_list": [
                    {
                        "model": "gpt-3.5-turbo",
                        "api_key": os.getenv("OPENAI_API_KEY")
                    }
                ]
            }
        )

    def get_agent(self):
        return self.agent
