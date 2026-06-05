# agent.py
import json
import logging
import os
import re
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from groq import Groq

from conversation import SYSTEM_PROMPT, is_greeting

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

_WORKOUT_SCHEMA = (
    '{"workout_title": "string", "notes": "string", '
    '"exercises": [{"name": "string", "sets": integer, '
    '"reps": "string", "weight_kg": float, "rest_seconds": integer}]}'
)


def generate_workout_plan(
    user_input: str,
    equipment_mode: str = "gym",
) -> dict:
    """
    Build a structured workout and return a parsed dict.

    Schema:
      {
        "workout_title": str,
        "notes": str,
        "exercises": [
          {"name": str, "sets": int, "reps": str,
           "weight_kg": float, "rest_seconds": int}
        ]
      }

    Raises ValueError if the LLM response cannot be parsed as JSON.
    """
    from database import get_exercises_by_category, supabase

    upper = get_exercises_by_category("Upper",     equipment=equipment_mode) or []
    lower = get_exercises_by_category("Lower",     equipment=equipment_mode) or []
    core  = get_exercises_by_category("Core",      equipment=equipment_mode) or []
    full  = get_exercises_by_category("Full Body", equipment=equipment_mode) or []
    all_ex = upper + lower + core + full

    user_stats = (
        supabase.table("user_progress").select("*").execute().data
        if supabase else []
    )

    prompt = (
        f"Equipment mode: {equipment_mode}.\n"
        f"Available exercises (use ONLY from this list): {all_ex}\n"
        f"User strength levels: {user_stats}\n\n"
        f"User request: '{user_input}'\n\n"
        "Instructions:\n"
        "1. Select 4-6 exercises from the list that match the request.\n"
        "2. Do NOT invent exercises not in the list.\n"
        "3. Calibrate weight_kg from the user's logged strength levels.\n"
        "4. For bodyweight exercises set weight_kg to 0.0.\n"
        "5. Apply progressive overload relative to logged weights.\n"
        "6. Do NOT provide a multi-day split unless explicitly asked.\n"
        f"7. Respond ONLY with a JSON object matching this schema:\n{_WORKOUT_SCHEMA}"
    )

    response = client.chat.completions.create(
        messages=[
            {"role": "system",
             "content": "You are a literal, goal-oriented strength coach. "
                        "Respond only with valid JSON."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned invalid JSON: {exc}\nRaw: {raw}"
        ) from exc


def _format_workout_markdown(workout: dict) -> str:
    """Convert a structured workout dict into a clean markdown table."""
    lines = []
    title    = workout.get("workout_title", "Your Workout")
    notes    = workout.get("notes", "")
    exercises = workout.get("exercises", [])

    lines.append(f"### {title}")
    if notes:
        lines.append(f"_{notes}_\n")

    if exercises:
        lines.append("| Exercise | Sets | Reps | Weight | Rest |")
        lines.append("|---|---|---|---|---|")
        for ex in exercises:
            name   = ex.get("name", "")
            sets   = ex.get("sets", "")
            reps   = ex.get("reps", "")
            weight = ex.get("weight_kg", 0.0)
            rest   = ex.get("rest_seconds", 60)
            w_str  = f"{weight}kg" if weight else "Bodyweight"
            lines.append(f"| {name} | {sets} | {reps} | {w_str} | {rest}s |")

    return "\n".join(lines)


def analyse_performance(exercise: str,
                        reps: int,
                        target: int,
                        weight: float) -> float:
    """
    Determine the next weight based on progressive overload rules.
    Returns the new weight as a float.
    """
    prompt = (
        f"User did {reps} reps of {exercise}. Goal: {target} @ {weight}kg. "
        "Rule: If reps >= target, add 2.5. If less, stay same. "
        "Return ONLY the final number. No text or units."
    )

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0,
    )

    raw_content = response.choices[0].message.content.strip()
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", raw_content)
    return float(numbers[-1]) if numbers else float(weight)


def _history_to_messages(
        history: List[dict], max_turns: int = 8) -> List[dict]:
    """
    Convert session history into the chat messages format for the Groq API.
    Keeps only the last `max_turns` turns to limit token usage.
    """
    if not history:
        return []
    msgs: List[dict] = []
    for turn in history[-max_turns:]:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        if role not in ("user", "assistant", "system"):
            role = "user"
        msgs.append({"role": role, "content": content})
    return msgs


def _looks_like_workout_request(text: str) -> bool:
    """Simple heuristic to detect workout intent."""
    if not text:
        return False
    low = text.lower()
    keywords = {
        "workout", "session", "upper", "lower", "full-body", "full body",
        "leg", "upper body", "lower body", "push", "pull", "squat", "deadlift",
        "bench", "press", "routine", "training", "programme", "program",
        "core", "abs", "bodyweight", "exercise", "exercises",
    }
    return any(k in low for k in keywords)


def generate_reply(
    user_input: str,
    history: Optional[List[dict]] = None,
    equipment_mode: str = "gym",
) -> Tuple[str, Optional[dict]]:
    """
    Conversation-aware wrapper. Returns (display_text, workout_dict).
    workout_dict is None for non-workout replies.

    Routing:
    - Short greetings handled locally (no LLM call).
    - Workout-like requests go to generate_workout_plan() → structured JSON.
    - All other inputs use multi-turn chat with SYSTEM_PROMPT + history.
    - Falls back to generate_workout_plan() if the chat call fails.
    """
    if not user_input:
        return "Hi — how can I help you train today?", None

    if is_greeting(user_input):
        return "Hey — ready to train? What would you like to do today?", None

    if _looks_like_workout_request(user_input):
        try:
            workout = generate_workout_plan(user_input, equipment_mode=equipment_mode)
            return _format_workout_markdown(workout), workout
        except Exception as exc:
            logging.warning("generate_workout_plan failed: %s", exc)

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
        return resp.choices[0].message.content.strip(), None
    except Exception as exc:
        logging.warning("generate_reply chat failed: %s", exc)
        try:
            workout = generate_workout_plan(user_input, equipment_mode=equipment_mode)
            return _format_workout_markdown(workout), workout
        except Exception as exc2:
            logging.warning("generate_workout_plan fallback failed: %s", exc2)
            return (
                "Sorry, I had trouble thinking that through — try rephrasing "
                "or try again in a moment.",
                None,
            )


if __name__ == "__main__":
    print("--- Generating Workout via Groq ---")
    try:
        workout = generate_workout_plan("Give me an upper body session")
        print(json.dumps(workout, indent=2))
    except Exception as exc:
        print(f"Error: {exc}")
