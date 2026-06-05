# database.py
import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

URL: str = os.environ.get("SUPABASE_URL", "")
KEY: str = os.environ.get("SUPABASE_KEY", "")
supabase: Optional[Client] = create_client(URL, KEY) if URL and KEY else None


def get_exercises_by_category(
    category: str,
    equipment: Optional[str] = None,
) -> Optional[List[Dict]]:
    """Fetch exercises by category, optionally filtered by equipment mode."""
    if not supabase:
        return None
    query = supabase.table("exercises").select("*").eq("category", category)
    if equipment:
        query = query.in_("equipment", [equipment, "both"])
    return query.execute().data


def get_user_stats(exercise_name: str) -> Optional[List[Dict]]:
    """Get weight/reps for a specific exercise from user_progress."""
    if not supabase:
        return None
    table = supabase.table("user_progress")
    response = table.select("*").eq("exercise_name", exercise_name).execute()
    return response.data if response.data else None


def update_weight(exercise_name: str, new_weight: float) -> None:
    """Update weight or create new record using on_conflict."""
    if not supabase:
        return
    table = supabase.table("user_progress")
    table.upsert(
        {"exercise_name": exercise_name, "current_weight": new_weight},
        on_conflict="exercise_name",
    ).execute()


def save_message(user_id: Optional[str],
                 role: str,
                 content: str) -> None:
    """Persist a chat message to the `messages` table."""
    if not supabase:
        return
    supabase.table("messages").insert(
        {"user_id": user_id, "role": role, "content": content}
    ).execute()


def get_recent_messages(user_id: Optional[str],
                        limit: int = 50) -> List[Dict]:
    """
    Retrieve recent messages ordered by created_at desc.
    Uses .is_() for null user_id to avoid PostgREST filter-drop on None.
    """
    if not supabase:
        return []
    query = supabase.table("messages").select("role, content, created_at")
    if user_id is None:
        query = query.is_("user_id", "null")
    else:
        query = query.eq("user_id", user_id)
    resp = query.order("created_at", desc=True).limit(limit).execute()
    return resp.data or []


if __name__ == "__main__":
    print("Testing connection...")
    test_data = get_exercises_by_category("Upper")
    print(f"Successfully fetched {len(test_data or [])} exercises!")
