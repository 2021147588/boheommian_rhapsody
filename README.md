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









---

## about the "lightrag" folder
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


##  Getting Started with Upstage Document parsing + LightRAG + Upstage Embedding

This guide explains how to set up and use LightRAG with Upstage API for PDF document indexing, vector & graph embedding, and RAG querying.

---

###  Prerequisites

- Python environment (e.g., conda, venv)
```bash
cd lightrag
```
- Install dependencies:

```bash
pip install -r requirements.txt
```

- `.env` file must exist in the **project root** directory and include:

```env
LLM_BINDING=openai
LLM_MODEL=solar-pro
LLM_BINDING_HOST=https://api.upstage.ai/v1
LLM_BINDING_API_KEY=your-upstage-api-key

EMBEDDING_BINDING=openai
EMBEDDING_MODEL=embedding-query
EMBEDDING_BINDING_HOST=https://api.upstage.ai/v1
EMBEDDING_BINDING_API_KEY=your-upstage-api-key
EMBEDDING_DIM=1024
```

- Place your PDF documents in the `./docs/` folder.

---

### 📄 Step 1: Parse and Preprocess PDF Files

This script reads all PDF files from `./docs/`, extracts text via Upstage API, and saves them as `.txt` in `./processed/`.

```bash
python process_document.py
```

> ✅ Only needed once, or when adding new PDFs.

---

### 🔧 Step 2: Start LightRAG Server (With Initial Indexing)

Starts the server and **automatically indexes** all text files into the vector DB and graph DB.

```bash
lightrag-server --input-dir ./processed --working-dir ./my_server_data --auto-scan-at-startup
```

- `--input-dir`: where processed `.txt` files are located
- `--working-dir`: where vector DB, graph DB, and metadata will be stored
- `--auto-scan-at-startup`: triggers indexing on server launch

Once indexing is done, LightRAG will stay running and listen for API and Web UI queries.

---

###  Step 3: Restart Server (Without Re-indexing)

If documents are already indexed, you can restart without rescanning files:

```bash
lightrag-server --working-dir ./my_server_data
```

>  This is faster and loads previously indexed data.

---

###  Add New PDFs Later

1. Put new PDF files into `./docs/`
2. Run:

```bash
python process_document.py
```

3. Restart the server with auto-scan enabled:

```bash
lightrag-server --input-dir ./processed --working-dir ./my_server_data --auto-scan-at-startup
```

---

### 🌐 Access Points(default port is 9621 / our custom local port number is 8000)

- Web UI: [http://localhost:9621/webui](http://localhost:9621/webui)
- API (Swagger): [http://localhost:9621/docs](http://localhost:9621/docs)
- API (ReDoc): [http://localhost:9621/redoc](http://localhost:9621/redoc)

---

