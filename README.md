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











-> about the "lightrag" folder
how to access to the lightrag api server
- http://165.132.46.89:32133/webui/
- (require yonsei vpn/wifi or grok if you want to view)
- ![image](https://github.com/user-attachments/assets/18ff85c1-387e-4f8b-af8e-ca850c107d38)
- ![image](https://github.com/user-attachments/assets/418f23b0-4be1-4d4d-9d79-51a2708eb131)

if you want to run lightrag in local  follow the below slide or lightrag github instruction 
    cd lightrag -> git clone https://github.com/HKUDS/LightRAG.git
    
lightrag github : https://github.com/HKUDS/LightRAG
follow the instruction in the lightrag github readme

For more information about LightRAG Server, please refer to LightRAG Server.(https://github.com/HKUDS/LightRAG/blob/main/lightrag/api/README.md)

✅ Prerequisites
Python environment is set up (e.g., conda, venv, etc.)

Required libraries are installed:

bash
Copy
Edit
pip install -r requirements.txt
A valid .env file is present in the project root directory with the following keys:

LLM_BINDING, LLM_MODEL, LLM_BINDING_API_KEY

EMBEDDING_BINDING, EMBEDDING_MODEL, EMBEDDING_DIM

PORT, TOKEN_SECRET, etc.

PDF files to process are located in the ./docs directory.

📄 Step 1: Process PDF Documents
Purpose: Extract text from PDF files in the ./docs directory and save them as .txt files in the ./processed folder.

bash
Copy
Edit
python process_document.py
 Note: This uses the Upstage OCR and extraction APIs. Only run this again if you’ve added new PDF files.

 Step 2: Start LightRAG Server & Index
Purpose: Start the LightRAG server and index the processed .txt files into a vector store and knowledge graph.

bash
Copy
Edit
lightrag-server --input-dir ./processed --working-dir ./my_server_data --auto-scan-at-startup
--input-dir: Folder containing .txt files to index.

--working-dir: Folder where all LightRAG data (vector DB, graph DB, metadata) will be stored.

--auto-scan-at-startup: Automatically scans and indexes new documents on server start.

 After this step, the server runs on your configured port (default: http://localhost:9621) and is ready to serve API or Web UI queries.

 Step 3: Restarting the Server (Skip Re-indexing)
If the documents are already indexed, restart the server without scanning new files:

bash
Copy
Edit
lightrag-server --working-dir ./my_server_data
 Use this command for faster startup when no new documents have been added.

 Adding New PDFs Later
Add new files to the ./docs directory.

Re-run document processing:

bash
Copy
Edit
python process_document.py
Restart the server with auto-scan to re-index new .txt files:

bash
Copy
Edit
lightrag-server --input-dir ./processed --working-dir ./my_server_data --auto-scan-at-startup
🌐 Access the LightRAG Server
Web UI: http://localhost:9621/webui

API Docs (Swagger): http://localhost:9621/docs

API Docs (ReDoc): http://localhost:9621/redoc
