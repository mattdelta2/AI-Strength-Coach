# conversation.py
SYSTEM_PROMPT = (
    "You are an encouraging, concise AI strength coach. "
    "Keep replies friendly, short, and focused on training, "
    "logging, or small talk."
)

GREETING_SHORTCUTS = {"hi", "hello", "hey", "yo", "hiya", "sup", "howdy"}


def is_greeting(text: str) -> bool:
    """Return True for short greeting phrases handled locally."""
    return bool(text and text.strip().lower() in GREETING_SHORTCUTS)
