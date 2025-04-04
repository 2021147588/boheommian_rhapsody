# 🛠️ Boheommian Rhapsody

### 📌 Overview
Boheommian Rhapsody is an AI-driven insurance agent simulator built for the **Upstage X YBIGTA Hackathon**.  
This project aims to simulate personalized insurance recommendation conversations using multiple agents and analyze their performance based on the customer profile.

### 🚀 Key Features
- ✅ **Multi-Agent Dialogue Simulation**: Simulates conversations between a system and a customer using planner-based agents.
- ✅ **Dashboard Interface**: Visualizes success rate, agent activity, dialogue history, and plan distribution.
- ✅ **Graph + Vector Hybrid RAG**: Integrates LightRAG with Upstage Embedding API and GraphDB for insurance document retrieval.

### 🖼️ Demo / Screenshots
![screenshot](./assets/screenshot.png)

> Optional: [Demo Video](https://youtu.be/example)

---

### 🧩 Tech Stack
- **Frontend**: HTML/CSS, JS (served from FastAPI static files)
- **Backend**: Python (FastAPI)
- **Database**: MongoDB (cloud), ChromaDB (local vector DB)
- **Others**:
  - OpenAI API (Chat-based simulation)
  - Upstage API (Document embedding & parsing)
  - LangChain (Agent orchestration)
  - LightRAG (Hybrid RAG engine)

---

### 🏗️ Project Structure
```bash
BOHEOMMIAN_RHAPSODY
│  .env
│  .env.template
│  .gitignore
│  README.md
│  requirements.txt
│
├─agents
│  │  advanced_orchestrator.py
│  │  conversation.py
│  │  generate_analysis.py
│  │  orchestrator.py
│  │
│  ├─advanced_planner_agents
│  │  advanced_base_agent.py
│  │  graph_rag_agent.py
│  │  rag_agent.py
│  │  recommendation_agent.py
│  │  router_agent.py
│  │  sales_agent.py
│  │
│  └─user_agent
│        user_agent.py
├─app
│  │  main.py
│  │  view.py
│  │
│  └─static/
|
├─database
│  │  insurance_docs_database.py
│  │
│  ├─insurance_docs/
│  │
│  ├─simulation_result/
│  │
│  └─vector_db/
|
├─lightrag
│  │  lightrag.log
│  │  process_document.py
│  │  query_rag.py
│  │  rag.py
│  │  requirements.txt
│  │
│  ├─docs
│  │      LA02762001.pdf
│  │
│  ├─else
│  │      query.py
│  │      query_param
│  │
│  └─processed
│         LA02762001.txt
│
├─sample_data
│      conversation_analysis_report.json
│      person.json
│
└─utils
        logger.py

```

---
### 🔧 Setup & Installation

> **Python version**: 3.10

```bash
# 1. Clone the repository
git clone https://github.com/2021147588/boheommian_rhapsody.git
cd boheommian_rhapsody

# 2. Switch to dev branch and install dependencies
git switch dev
pip install -r requirements.txt

# 3. Create .env file (see .env.template for guidance)
cp .env.template .env

# 4. Set project path and run backend server
export PYTHONPATH=/your/local/path/to/boheommian_rhapsody
cd app
python main.py
```
✅ App will be available at: http://127.0.0.1:8001/static/index.html

---

### 🧠 App Description

#### ▶️ How to Run the Simulation

1. Click **"Run Simulation"**
2. Upload \`person.json\` (drag & drop or choose file)
   - 🧪 Sample \`person.json\` is in \`sample_data/\`
3. Set simulation options:
   - **Max Dialogue Turns**
   - **Sample Limit**
4. Click **"Run Simulation"**
5. ✅ View simulation results in the dashboard


#### 📊 How to Use the Dashboard

##### 🧾 Dashboard Section
- 🧍 Total customers
- ✅ Sign-up success count
- 📈 Success rate
- 🤖 Agent activity ratio
- 🔁 Turn-based success rate
- 🕵️‍♀️ Recent simulations

##### 💬 Conversation History Section
- Select customer
- View:
  - Profile
  - Dialogue log
  - Agent flow

##### 📈 Analysis Section
- 📦 Recommended plan distribution
- 🔄 Agent transition frequency
- 🎯 Success by customer traits
---

## 🔗 About LightRAG Integration

### 🌐 Access LightRAG Server
- Web UI: http://165.132.46.89:32133/webui/
- 🔐 Requires Yonsei VPN/WiFi or \`ngrok\`


### 📦 Setting Up LightRAG (Local)

```bash
cd lightrag
git clone https://github.com/HKUDS/LightRAG.git
pip install -r requirements.txt
```

Create a `.env` file in the root with the following:

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


### 📝 Step-by-Step Usage

1. Put PDFs in \`./docs/\`
2. Run:
```bash
python process_document.py
```

3. Launch server:
```bash
lightrag-server --input-dir ./processed --working-dir ./my_server_data --auto-scan-at-startup
```

4. Restart without re-indexing:
```bash
lightrag-server --working-dir ./my_server_data
```

---

### 🌐 LightRAG Access Points

| URL Type | Address |
|----------|---------|
| Web UI   | http://localhost:9621/webui |
| Swagger  | http://localhost:9621/docs |
| ReDoc    | http://localhost:9621/redoc |

More info: https://github.com/HKUDS/LightRAG


### 📁 Dataset & References

- **Dataset**: Sample customer profiles (\`person.json\`)

- **References**:  
  - [LightRAG](https://github.com/HKUDS/LightRAG)  
  - [Upstage API](https://docs.upstage.ai/)  
  - [LangChain](https://www.langchain.com/)

---

### 🙌 Team Members

| Name     | Role                    | GitHub                                |
|----------|-------------------------|---------------------------------------|
| 문찬우   | Team Lead & GraphDB     | [@urbanking](https://github.com/urbanking) |
| 정다연   | App & LLM Workflow & User Agent Modeling    | [@dayeon86](https://github.com/2021147588) |
| 고정훈   | LLM Workflow & Planner Agent Modeling  | [@hoonestly](https://github.com/hoonestly)       |
| 김성환   | Planner Agent Modeling & Conversation Analysis | [@seongmin-k](https://github.com/happysnail06) |
| 강정묵   | User Agent Modeling | [@Mookjsi](https://github.com/Mookjsi)|

---

### ⏰ Development Period

- 2025-03-29 ~ 2025-04-05  
  (Upstage × YBIGTA Hackathon)

---

### 📄 License

This project is licensed under the [MIT license](https://opensource.org/licenses/MIT).  
See the `LICENSE` file for more details.

---

### 💬 Additional Notes

- 📂 All local databases (Chroma, LightRAG vector store) are stored in the `./database/` folder  
- ⚙️ Make sure `.env` is configured properly for all modules  
- 🐛 If you encounter errors, refer to the logs printed in the backend console  

