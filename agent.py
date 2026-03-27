# agent.py
import os
import re
from typing import List, Optional

from dotenv import load_dotenv
from groq import Groq

from conversation import SYSTEM_PROMPT, is_greeting

load_dotenv()

# Setup Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def generate_workout_plan(user_input: str) -> str:
    """
    Build a structured workout using the DB and return the raw assistant text.

    This function is the canonical source for workout outputs and MUST include
    the hidden EXERCISES tag in the format:
      <!-- EXERCISES: ['Exercise A', 'Exercise B'] -->
    so the UI can extract exercise names for logging.
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
        "1. ONLY generate a workout for the SPECIFIC category "
        "requested in the "
        "LATEST USER REQUEST. If they ask for 'Lower Body', do NOT "
        "include any "
        "Upper Body exercises like Bench Press or Curls.\n"
        "2. Do NOT provide a multi-day split unless explicitly asked.\n"
        "3. Follow the 'No Machines' rule if mentioned. Substitute silently.\n"
        "4. Use the Big 3 history to calibrate weights.\n"
        "5. End with the hidden tag: <!-- EXERCISES: ['Name','Name'] -->"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a literal, "
                "goal-oriented trainer."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content


def analyse_performance(exercise: str,
                        reps: int,
                        target: int,
                        weight: float) -> float:
    """
    Determine the next weight based on progressive overload rules.

    South African English spelling used for function name (analyse).
    """
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


def _history_to_messages(
        history: List[dict], max_turns: int = 8) -> List[dict]:
    """
    Convert session history (list of {"role","content"}) into the chat
    messages format expected by the Groq chat API. Keeps only the last
    `max_turns` turns to limit token usage.
    """
    if not history:
        return []
    recent = history[-max_turns:]
    msgs: List[dict] = []
    for turn in recent:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        if role not in ("user", "assistant", "system"):
            role = "user"
        msgs.append({"role": role, "content": content})
    return msgs


def _looks_like_workout_request(text: str) -> bool:
    """Simple heuristic to detect workout intent 
    (keeps routing deterministic)."""
    if not text:
        return False
    low = text.lower()
    keywords = {
        "workout", "session", "upper", "lower", "full-body", "full body",
        "leg", "upper body", "lower body", "push", "pull", "squat", "deadlift",
        "bench", "press", "routine", "training", "programme", "program"
    }
    return any(k in low for k in keywords)


def generate_reply(user_input: str,
                   history: Optional[List[dict]] = None) -> str:
    """
    Conversation-aware wrapper.

    Behaviour:
    - Short greetings handled locally (no LLM call).
    - Workout-like requests are routed to generate_workout_plan(...) to ensure
      the structured EXERCISES tag is present for extraction.
    - Other inputs use the multi-turn chat path with SYSTEM_PROMPT 
    and recent history.
    - Falls back to the structured generator on chat API failure.
    """
    if not user_input:
        return "Hi — how can I help you train today?"

    if is_greeting(user_input):
        # South African English phrasing
        return "Hey — ready to train? What would you like to do today?"

    # Route workout intent to the structured generator to 
    # preserve EXERCISES tag
    if _looks_like_workout_request(user_input):
        try:
            return generate_workout_plan(user_input)
        except Exception:
            # If the specialised generator fails, fall back to chat below
            pass

    history = history or []
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(_history_to_messages(history, max_turns=8))
    messages.append({"role": "user", "content": user_input})

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            max_tokens=512,
        )
        assistant_text = resp.choices[0].message.content.strip()
        return assistant_text
    except Exception:
        # If the chat call fails, try the specialised workout generator
        try:
            return generate_workout_plan(user_input)
        except Exception:
            return (
                "Sorry, I had trouble thinking that through — try rephrasing "
                "or try again in a moment."
            )


if __name__ == "__main__":
    print("--- Generating Workout via Groq ---")
    try:
        workout = generate_workout_plan("Give me an upper body session")
        print(workout)
    except Exception as exc:
        print(f"Error: {exc}")
