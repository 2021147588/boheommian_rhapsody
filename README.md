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


Prerequisites:
Python environment is set up, and required libraries are installed (pip install -r requirements.txt).
A correct .env file exists in the project root directory with necessary API keys and configurations (API keys, LLM_..., EMBEDDING_..., PORT, EMBEDDING_DIM, etc.).
For the initial run: PDF files to be processed are present in the docs directory (or another specified input directory).
Step 1: Process PDF Documents and Extract Text (Run initially or when adding new PDFs)
Purpose: Reads PDF files from the docs folder, processes them using the Upstage API (as defined in the script), and saves the extracted and cleaned text as .txt files in the processed folder.
Terminal Command (in the project root directory):
Apply to lightrag.log
Run
(Wait for this command to complete successfully. It creates the .txt input files for the next step.)
Step 2: Start LightRAG Server & Initial Indexing (Run for the very first time or after clearing data)
Purpose: Starts the LightRAG server, reads the .txt files from the processed folder (created in Step 1), builds the vector database and knowledge graph, and saves all data into the my_server_data directory. After indexing, the server becomes ready to accept API queries.
Terminal Command (in the project root directory, after Step 1 is complete):
Apply to lightrag.log
Run
--input-dir ./processed: Specifies the directory containing the text files from Step 1.
--working-dir ./my_server_data: Specifies the directory where LightRAG will store all its data (vector DB, graph, cache, etc.). It will be created if it doesn't exist.
--auto-scan-at-startup: Tells the server to automatically scan the input directory and index any new files found when it starts. Essential for the first run.
Result: The server starts, indexes the data (logs will appear in the terminal), and then stays running, listening for API requests on the configured port (e.g., 9621). Keep this terminal window open to keep the server running.
Step 3: Restarting the LightRAG Server (Use this if indexing is already complete)
Purpose: If you have previously completed Step 1 and Step 2, and the vector database/knowledge graph already exists in my_server_data, you can restart the server without re-processing the PDFs or re-indexing everything. The server will load the existing data.
Terminal Command (in the project root directory):
Apply to lightrag.log
Run
Note: We only specify the --working-dir. The server will automatically load the data found there. We typically don't need --input-dir or --auto-scan-at-startup unless we specifically want to index new files added to processed after the last run.
Result: The server starts much faster as it loads the existing data from my_server_data and becomes ready to accept API queries on the configured port. Keep the terminal open.
In Summary:
First time: Run python process_document.py, then lightrag-server --input-dir ./processed --working-dir ./my_server_data --auto-scan-at-startup.
Restarting later: Just run lightrag-server --working-dir ./my_server_data.
Adding new PDFs later: Run python process_document.py (it should only process the new PDFs if the .txt files for old ones already exist in processed), then restart the server using Step 2's command (lightrag-server --input-dir ./processed --working-dir ./my_server_data --auto-scan-at-startup) so it picks up the new .txt files.

