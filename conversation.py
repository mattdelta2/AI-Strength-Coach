# conversation.py
import re
from typing import Optional

SYSTEM_PROMPT = (
    "You are an encouraging, concise AI strength coach. "
    "You support two training modes: gym (barbells, cables, machines) and "
    "home (bodyweight and minimal equipment). "
    "When generating a workout you respond with structured JSON. "
    "For all other replies keep answers friendly, short, and focused on "
    "training, progress, or small talk. "
    "You apply progressive overload: always reference the user's logged "
    "weights when prescribing loads."
)

GREETING_SHORTCUTS = {"hi", "hello", "hey", "yo", "hiya", "sup", "howdy"}

_HOME_PATTERN = re.compile(
    r"\b(home|bodyweight|body weight|no equipment|no gym|"
    r"without equipment|outside|park|apartment)\b",
    re.IGNORECASE,
)
_GYM_PATTERN = re.compile(
    r"\b(gym|barbell|cable|machine|rack|weights|dumbbell)\b",
    re.IGNORECASE,
)


def is_greeting(text: str) -> bool:
    """Return True for short greeting phrases handled locally."""
    return bool(text and text.strip().lower() in GREETING_SHORTCUTS)


def detect_equipment_mode(text: str) -> Optional[str]:
    """
    Return 'home' or 'gym' if the text signals an equipment preference,
    otherwise return None (no change to current mode).
    Home signals take priority over gym signals.
    """
    if not text:
        return None
    if _HOME_PATTERN.search(text):
        return "home"
    if _GYM_PATTERN.search(text):
        return "gym"
    return None
