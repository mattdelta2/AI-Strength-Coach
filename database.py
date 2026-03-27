# database.py
import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

URL: str = os.environ.get("SUPABASE_URL", "")
KEY: str = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(URL, KEY)


def get_exercises_by_category(category: str) -> Optional[List[Dict]]:
    """Fetch exercises from DB based on Upper/Lower/Full Body."""
    table = supabase.table("exercises")
    response = table.select("*").eq("category", category).execute()
    return response.data


def get_user_stats(exercise_name: str) -> Optional[List[Dict]]:
    """Get weight/reps for a specific exercise from user_progress."""
    table = supabase.table("user_progress")
    response = table.select("*").eq("exercise_name", exercise_name).execute()
    return response.data if response.data else None


def update_weight(exercise_name: str, new_weight: float) -> None:
    """Update weight or create new record using on_conflict."""
    table = supabase.table("user_progress")
    table.upsert(
        {"exercise_name": exercise_name, "current_weight": new_weight},
        on_conflict="exercise_name",
    ).execute()


def save_message(user_id: Optional[str],
                 role: str,
                 content: str) -> None:
    """
    Persist a chat message to the `messages` table.
    `user_id` may be None for anonymous users.
    """
    if not supabase:
        return
    supabase.table("messages").insert(
        {"user_id": user_id, "role": role, "content": content}
    ).execute()


def get_recent_messages(user_id: Optional[str],
                        limit: int = 50) -> List[Dict]:
    """
    Retrieve recent messages for a user ordered by created_at desc.
    Returns an empty list if no supabase client is configured.
    """
    if not supabase:
        return []
    resp = (
        supabase.table("messages")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data or []


if __name__ == "__main__":
    print("Testing connection...")
    test_data = get_exercises_by_category("Upper")
    print(f"Successfully fetched {len(test_data)} exercises!")
