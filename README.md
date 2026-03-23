# 🏋️ AI Strength Coach Agent  
*Your autonomous personal trainer powered by Groq.*

![Python](https://img.shields.io/badge/python-3.11.9-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.x-brightgreen.svg)
![Supabase](https://img.shields.io/badge/supabase-postgres-green.svg)
![Groq](https://img.shields.io/badge/groq-llama3-orange.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

<img width="3840" height="1980" alt="AI_Agent_Image" src="https://github.com/user-attachments/assets/3838538c-eea5-48e2-a72c-53d2a0abdded" />

*Interactive logging cards in Streamlit UI.*

---

## 🌟 Features  
- **Plans workouts conversationally**: Translates natural language into structured sessions.  
- **Estimates weights intelligently**: Calibrates intensity using “Big 3” (Squat, Bench, Deadlift) ratios.  
- **Substitutes seamlessly**: Swaps machine movements for free‑weight alternatives without breaking context.  
- **Logs sessions automatically**: Parses hidden metadata with RegEx to generate sidebar logging forms.  
- **Learns persistently**: Stores strength history in **Supabase (Postgres)** to evolve workouts over time.  

---

## 🛠️ Tech Stack  
- **LLM Engine**: Groq (Llama 3.3‑70B)  
- **Database**: Supabase (PostgreSQL)  
- **Frontend**: Streamlit  
- **Logic**: Python (SDKs + Regex)  

---

## 🧠 Agentic Loop  
The agent follows a **Plan → Execute → Analyse → Update** cycle:  
1. **Plan**: Retrieves exercises and estimates weights from history.  
2. **Execute**: User performs session; UI provides interactive logging cards.  
3. **Analyse**: Evaluates reps/weights against targets.  
4. **Update**: Database stores new “Working Weights” for next session.   

---

## ⚠️ Environment Requirements
This project was tested and runs reliably on **Python 3.11.9**.  
Due to NumPy compatibility issues, earlier or later versions of Python may not work correctly.  
Make sure to install Python 3.11.9 before setting up the environment.  
**Recommended tools**: `pyenv` or `conda` to manage Python versions and virtual environments.

---

## ⚙️ Quick Start  
```bash
# 1. Clone the repo
git clone https://github.com/mattdelta2/AI-Strength-Coach.git
cd AI-Strength-Coach

# 2. Ensure correct Python version
# Use pyenv or conda to install/use Python 3.11.9
pyenv install 3.11.9
pyenv local 3.11.9

# 3. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize database
# Run schema.sql in Supabase SQL Editor (see Getting Your Supabase URL and Key)

# 6. Configure secrets
# Add to .env (see Getting Your Groq API Key and Getting Your Supabase URL and Key)
# Example .env shown below

# 7. Run the app
streamlit run app.py
```

---

## 📂 Example `.env`  
```env
SUPABASE_URL=https://xyzcompany.supabase.co
SUPABASE_KEY=your-service-role-key
GROQ_API_KEY=your-groq-key
```

---

## 🔑 Getting Your Groq API Key  
To run this project, you’ll need a Groq API key.  
Create an account and generate an API key at: https://console.groq.com  
Add the key to your `.env` as `GROQ_API_KEY`.

---

## 🔑 Getting Your Supabase URL and Key  
You’ll need a Supabase project to store workout history:

1. Sign up at https://supabase.com and create a new project.  
2. In the project dashboard copy the **Project URL** — this is your `SUPABASE_URL`.  
3. Go to **Project Settings → API** and copy the **Service Role Key** — this is your `SUPABASE_KEY`.  
   - **Important**: The service role key has elevated privileges. Use it only for local development or trusted server environments. For public or client‑side apps, use the anon key with appropriate RLS policies.  
4. Add both values to your `.env` as shown above.

---

## ✅ Setup Checklist
- [ ] Install Python 3.11.9 (pyenv or conda recommended)  
- [ ] Create and activate a virtual environment  
- [ ] `pip install -r requirements.txt`  
- [ ] Create Supabase project and run `schema.sql`  
- [ ] Add `SUPABASE_URL`, `SUPABASE_KEY`, `GROQ_API_KEY` to `.env`  
- [ ] `streamlit run app.py`

---

## 📜 Database Schema  
```sql
CREATE TABLE exercises (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  category TEXT,
  target_muscle TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE user_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  exercise_id UUID REFERENCES exercises(id),
  current_weight FLOAT,
  target_reps INTEGER,
  recorded_at TIMESTAMP DEFAULT now(),
  UNIQUE(user_id, exercise_id)
);
```

---

## 🔒 Security & Privacy  
- **Never commit secrets** (`SUPABASE_KEY`, `GROQ_API_KEY`, `.env`).  
- Use role‑based Supabase keys with least privilege in production.  
- For public deployments, enable Row Level Security and use anon keys with server‑side functions for sensitive operations.  
- Data stored only for workout history.

---

## 📜 Medical Disclaimer  
This AI agent provides general fitness information for educational purposes only and is not a substitute for professional medical advice. Always consult with a healthcare provider before starting a new exercise programme. Use proper form to avoid injury and verify that suggested weights and movements are appropriate for your level. 

---

## 🐛 Known Issues / Troubleshooting

- **Python Version**  
  This project requires **Python 3.11.9** for NumPy compatibility. Other versions may cause dependency errors. If you encounter issues, install Python 3.11.9 and recreate your virtual environment.

- **Environment Variables**  
  Ensure your `.env` file is correctly configured with `SUPABASE_URL`, `SUPABASE_KEY`, and `GROQ_API_KEY`. Missing or incorrect values will prevent the app from connecting to Supabase or Groq.

- **Supabase Permissions**  
  If you see permission errors when writing to the DB, verify you used the Service Role Key for local dev and that your tables and policies are set up correctly.

- **Streamlit Reruns**  
  Streamlit automatically reruns the script when state changes. If you see unexpected behaviour, clear session state (`🗑️ Clear Chat History` in the sidebar) or restart the app.

- **NumPy / Binary Wheels**  
  If `pip install` fails on NumPy, ensure your Python version is 3.11.9 and that you have a compatible pip/wheel environment. Installing from prebuilt wheels or using `pip install --upgrade pip setuptools wheel` can help.

---

## 🤝 Contributing  
Pull requests welcome! Please open issues for bugs or feature requests. If you submit a PR that requires new environment variables or schema changes, update this README accordingly.

---

## 📄 Licence  
MIT Licence — free to use and modify.
