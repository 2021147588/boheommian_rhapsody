# boheommian_rhapsody

Upstage X YBIGTA Hackathon Project

## How to Run

### Set Up Environment

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
    export PYTHONPATH= **/your/local/path/to/boheommian_rhapsody** # example: /Users/happy/Desktop/boheommian_rhapsody/ 
    cd backend
    python main.py
    ```

- ✅ The app will be available at:  
  [http://127.0.0.1:8001/static/index.html](http://127.0.0.1:8001/static/index.html)

- 🧪 We provide a test sample file, `person.json`, located in the root directory.  
  You can use this file to simulate user inputs and test the application. The results will be stored in **agents/results** 

