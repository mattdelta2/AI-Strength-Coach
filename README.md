# AI Strength Coach Agent

An autonomous workout agent that generates personalized training sessions and 
dynamically adjusts weights based on user performance.

## Features
- **Intelligent Workout Generation**: Pulls from a Supabase PostgreSQL library 
  to build balanced Upper/Lower/Full-body sessions.
- **Autonomous Progression**: Uses Llama 3.3 (via Groq) to analyze rep counts 
  and automatically calculate progressive overload or deloading.
- **Persistent Memory**: Stores strength history in Supabase to ensure 
  workouts evolve over time.
- **Clean Code**: Fully PEP 8 / Flake8 compliant architecture.

## Tech Stack
- **AI Engine**: Groq (Llama 3.3-70B)
- **Database**: Supabase (PostgreSQL)
- **Frontend**: Streamlit
- **Logic**: Python (Native SDKs)

## Setup
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`
3. Add your `SUPABASE_URL`, `SUPABASE_KEY`, and `GROQ_API_KEY` to a `.env` file.
4. Run the app: `streamlit run app.py`

## The Agentic Loop
The agent follows a **Plan -> Execute -> Analyze -> Update** cycle:
1. **Plan**: Selects exercises based on category.
2. **Execute**: User performs the workout.
3. **Analyze**: AI evaluates performance vs. targets.
4. **Update**: Database is updated with new "Working Weights" for the next session.
