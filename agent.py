import os
import re

from groq import Groq
from dotenv import load_dotenv


load_dotenv()

# Setup Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def generate_workout_plan(user_input):
    """
    AI parses user words and builds a workout from the database.
    
    Updated with 'Strict Adherence' to prevent context drift.
    """
    from database import get_exercises_by_category, supabase

    # Fetch library and user stats
    upper = get_exercises_by_category("Upper")
    lower = get_exercises_by_category("Lower")
    all_ex = (upper if upper else []) + (lower if lower else [])
    user_stats = supabase.table("user_progress").select("*").execute().data

    prompt = (
        f"You are a professional Strength Coach. DB Exercises: {all_ex}\n"
        f"User's Strength Levels: {user_stats}\n\n"
        f"LATEST USER REQUEST: '{user_input}'\n\n"
        "STRICT INSTRUCTIONS:\n"
        "1. ONLY generate a workout for the "
        "SPECIFIC category requested in the "
        "LATEST USER REQUEST. If they ask for 'Lower Body', do NOT include "
        "any Upper Body exercises like Bench Press or Curls.\n"
        "2. Do NOT provide a multi-day split unless explicitly asked.\n"
        "3. Follow the 'No Machines' rule if mentioned. Substitute silently.\n"
        "4. Use the Big 3 history to calibrate weights.\n"
        "5. End with the hidden tag: <!-- EXERCISES: [Name, Name] -->"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": 
             "You are a literal, goal-oriented trainer."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content


def analyze_performance(exercise, reps, target, weight):
    """AI determines the next weight based on progressive overload rules."""
    prompt = (
        f"User did {reps} reps of {exercise}. Goal: {target} @ {weight}kg. "
        "Rule: If reps >= target, add 2.5. If less, stay same. "
        "Return ONLY the final number. No text or units."
    )

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0,
    )

    raw_content = chat_completion.choices[0].message.content.strip()
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", raw_content)

    return float(numbers[-1]) if numbers else float(weight)


if __name__ == "__main__":
    print("--- Generating Workout via Groq ---")
    try:
        WORKOUT = generate_workout_plan("Give me an upper body session")
        print(WORKOUT)
    except Exception as e:
        print(f"Error: {e}")
