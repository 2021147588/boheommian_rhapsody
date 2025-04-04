# boheommian_rhapsody

Upstage X YBIGTA Hackathon Project

## How to Run

- > **Python version**: 3.10 


- Clone the repository
    ```bash
    git clone https://github.com/2021147588/boheommian_rhapsody.git
    ```
    
- Switch to dev and run:
    ```bash
    git switch dev
    pip install -r requirements.txt
    ```


- Create a .env file in the root directory and add your API keys:

    ```bash
    OPENAI_API_KEY=your_openai_api_key_here
    UPSTAGE_API_KEY=your_upstage_api_key_here
    ```

- To run the code:
    ```bash
    export PYTHONPATH= **/your/local/path/to/boheommian_rhapsody**
    # example: /Users/happy/Desktop/boheommian_rhapsody/ 
    cd backend
    python main.py
    ```

- ✅ The app will be available at:  
  [http://127.0.0.1:8001/static/index.html](http://127.0.0.1:8001/static/index.html)

- 🧪 We provide a test sample file, `person.json`, located in the root directory.  
  You can use this file to simulate user inputs and test the application. The results will be stored in **agents/results** 

- To analyze the simulation results, run 
    ```bash
    python generate_analysis.py
    ```











+
access to the lightrag api server
- http://165.132.46.89:32133/webui/
- (require yonsei vpn/wifi or grok if you want to view)
- ![image](https://github.com/user-attachments/assets/18ff85c1-387e-4f8b-af8e-ca850c107d38)
- ![Uploading image.png…]()
- if you want to run lightrag in your computer follow the below slide or lightrag github instruction 
-lightrag github : https://github.com/HKUDS/LightRAG
- Install LightRAG Core
Install from source (Recommend)
cd LightRAG
pip install -e .
Install from PyPI
pip install lightrag-hku
Install LightRAG Server
The LightRAG Server is designed to provide Web UI and API support. The Web UI facilitates document indexing, knowledge graph exploration, and a simple RAG query interface. LightRAG Server also provide an Ollama compatible interfaces, aiming to emulate LightRAG as an Ollama chat model. This allows AI chat bot, such as Open WebUI, to access LightRAG easily.

Install from PyPI
pip install "lightrag-hku[api]"
Installation from Source
# create a Python virtual enviroment if neccesary
# Install in editable mode with API support
pip install -e ".[api]"
For more information about LightRAG Server, please refer to LightRAG Server.(https://github.com/HKUDS/LightRAG/blob/main/lightrag/api/README.md)


