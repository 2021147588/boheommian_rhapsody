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


## App Description

### How to Run the Simulation

1. Click on the **"Run Simulation"** menu.
2. Upload the `person.json` file.  
   - You can drag and drop the file or click the **"Choose File"** button to select it.
   - 🧪 We provide a test sample file, `person.json`, located in the `sample_data` directory.  

3. Configure the desired simulation options:
   - **Max Dialogue Turns**: Maximum number of dialogue turns during the simulation  
   - **Sample Limit**: Number of customer data entries to process (`0 = All`)
4. Click the **"Run Simulation"** button.
5. ✅ Once the simulation is complete, check the results.

---

### 📊 How to Use the Dashboard

#### 🧾 Dashboard Section

Displays summary information of the **most recent simulation**:
- 🧍 **Total number of customers**
- ✅ **Number of successful sign-ups**
- 📈 **Success rate**
- 🤖 **Agent activity ratio**
- 🔁 **Success rate by dialogue turn**
- 🕵️‍♀️ **List of recently simulated customers**

---

#### 💬 Conversation History Section

Allows you to view the **conversation history of a specific customer**:

1. Select a customer from the dropdown menu.  
2. View that customer’s:
   - Profile  
   - Conversation history  
   - Agent activities  

---

#### 📊 Analysis Section

Provides **in-depth analysis** of simulation results:
- 📦 **Distribution of recommended plans**
- 🔄 **Frequency of agent transitions**
- 🎯 **Success rate by customer characteristics**

