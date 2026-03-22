This is a strong, clean README that clearly outlines the project. To make it truly "Senior Portfolio" grade, we should add the Advanced Logic we built at the end (the Hidden Metadata and the "Big 3" Scaling). These are the parts that prove you aren't just using a chatbot, but building an actual intelligent system.
Here is an updated version you can copy and paste:

# 🏋️ AI Strength Coach Agent
A stateful AI Agent designed to act as an autonomous personal trainer. It doesn't just generate text; it **reasons** through your strength history to provide optimal weights and progressive overload.

---<img width="3840" height="1980" alt="AI_Agent_Image" src="https://github.com/user-attachments/assets/c2912936-f409-4364-8298-015e8d5c893e" />
## 🌟 Key Features- **Conversational Planning**: Uses Groq (Llama 3.3) to translate natural language requests into structured workouts.- **Intelligent Weight Estimation**: Calibrates intensity for new exercises based on the user's "Big 3" (Squat, Bench, Deadlift) ratios.- **Silent Substitution**: Automatically swaps machine-based movements for free-weight alternatives when requested, without breaking context.- **Automated Logging**: Uses RegEx to parse hidden metadata in AI responses, dynamically generating sidebar logging forms.- **Persistent Memory**: Stores strength history in **Supabase (Postgres)** to ensure workouts evolve over time.
## 🛠️ Tech Stack- **LLM Engine**: Groq (Llama 3.3-70B)- **Database**: Supabase (PostgreSQL)- **Frontend**: Streamlit- **Logic**: Python (Native SDKs + Regex)
## 🧠 The Agentic LoopThe agent follows a **Plan -> Execute -> Analyze -> Update** cycle:1. **Plan**: AI retrieves exercises from the DB and estimates weights based on historical data.2. **Execute**: User performs the session; UI provides interactive logging cards.3. **Analyze**: AI evaluates reps/weight performed against targets via a performance node.4. **Update**: Database is updated with new "Working Weights" for the next session.
## ⚙️ Setup1. **Clone the repo.**
2. **Install dependencies**: `pip install -r requirements.txt`3. **Initialize Database**: Run the provided SQL schema in your Supabase SQL Editor.
4. **Configure Secrets**: Add `SUPABASE_URL`, `SUPABASE_KEY`, and `GROQ_API_KEY` to a `.env` file.
5. **Run the app**: `streamlit run app.py`
## 📜 SQL Schema```sql
CREATE TABLE exercises (id UUID PRIMARY KEY, name TEXT, category TEXT, target_muscle TEXT);
CREATE TABLE user_progress (exercise_name TEXT UNIQUE, current_weight FLOAT, target_reps INTEGER);



**Medical Disclaimer:**
This AI agent provides general fitness information and is not a substitute for professional medical advice. Always consult with a healthcare provider before starting a new program. Verify that all suggested weights and movements are safe for your level.
