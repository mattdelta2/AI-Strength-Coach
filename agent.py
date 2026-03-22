import os

from groq import Groq
from dotenv import load_dotenv
from database import get_exercises_by_category
import re 


load_dotenv()

# Setup Groq Client (Fast, Stable, and Free)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def generate_workout_plan(category):
    """Fetch exercises from DB and use Groq to plan a workout."""
    exercises = get_exercises_by_category(category)

    prompt = (
        f"Exercises: {exercises}. Create a 3-exercise {category} workout. "
        "Include Name, Weight (20kg start), and Reps (10)."
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a strength coach."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
    )
    # FIX: Access the first choice in the list before calling .message
    return chat_completion.choices[0].message.content


def analyze_performance(exercise, reps, target, weight):
    """AI determines the next weight based on progressive overload rules."""
    prompt = (
        f"User did {reps} reps of {exercise}. Goal: {target} @ {weight}kg. "
        "Rule: If reps >= target, add 2.5. If less, stay same. "
        "Return ONLY the final number. No text, no units, no equals signs."
    )

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0,  # Setting to 0 makes the AI much more literal
    )
    
    raw_content = chat_completion.choices[0].message.content.strip()
    
    # Safety: Use Regex to find the last number in the string (the result)
    # This fixes the "20 + 2.5 = 22.5" issue by only grabbing the "22.5"
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", raw_content)
    if numbers:
        return float(numbers[-1])
    
    return float(weight)  # Fallback to current weight if AI fails


if __name__ == "__main__":
    print("--- Generating Workout via Groq ---")
    try:
        workout = generate_workout_plan("Upper")
        print(workout)
    except Exception as e:
        print(f"Error: {e}")
