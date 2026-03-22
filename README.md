# 🏋️ AI Strength Coach Agent  
*Your autonomous personal trainer powered by Groq.*

`https://github.com/user-attachments/assets/c2912936-f409-4364-8298-015e8d5c893e`  
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
The agent follows a **Plan → Execute → Analyze → Update** cycle:  
1. **Plan**: Retrieves exercises and estimates weights from history.  
2. **Execute**: User performs session; UI provides interactive logging cards.  
3. **Analyze**: Evaluates reps/weights against targets.  
4. **Update**: Database stores new “Working Weights” for next session.  

---

## ⚙️ Quick Start  
```bash
# 1. Clone the repo
git clone <your-repo-url>
cd ai-strength-coach

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
# Run schema.sql in Supabase SQL Editor

# 4. Configure secrets
# Add to .env
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
GROQ_API_KEY=your_key

# 5. Run the app
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
- Never commit secrets (`SUPABASE_KEY`, `GROQ_API_KEY`).  
- Use role‑based Supabase keys with least privilege.  
- Data stored only for workout history.  

---

## 📜 Medical Disclaimer  
This AI agent provides general fitness information and is **not** a substitute for professional medical advice. Always consult a healthcare provider before starting a new program. Verify that suggested weights and movements are safe for your level.  

---

## 🤝 Contributing  
Pull requests welcome!  

---

## 📄 License  
MIT License — free to use and modify.  

---

👉 This version is copy‑ready for your repo. Would you like me to also draft a **GitHub Actions CI workflow** (lint + test + badge) so your README can show build status at the top?
