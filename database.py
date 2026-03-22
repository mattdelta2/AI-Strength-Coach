import os

from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def get_exercises_by_category(category):
    """Fetch exercises from DB based on Upper/Lower/Full Body."""
    table = supabase.table("exercises")
    response = table.select("*").eq("category", category).execute()
    return response.data


def get_user_stats(exercise_name):
    """Get weight/reps for a specific exercise from user_progress."""
    table = supabase.table("user_progress")
    response = table.select("*").eq("exercise_name", exercise_name).execute()
    return response.data if response.data else None


def update_weight(exercise_name, new_weight):
    """Update weight or create new record using on_conflict."""
    table = supabase.table("user_progress")
    # Adding on_conflict tells Supabase which column is the unique key
    table.upsert(
        {"exercise_name": exercise_name, "current_weight": new_weight},
        on_conflict="exercise_name"
    ).execute()


if __name__ == "__main__":
    print("Testing connection...")
    test_data = get_exercises_by_category("Upper")
    print(f"Successfully fetched {len(test_data)} exercises!")
