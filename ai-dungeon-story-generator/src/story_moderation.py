"""
Basic content moderation utilities.
This is intentionally lightweight: it allows the project to run offline and to
catch obvious bad content.
For production, integrate a dedicated moderation API or service.
"""
from typing import List
import re

DEFAULT_BANNED = ["rape", "sex", "kill", "murder", "child", "porn", "incest"]

def simple_moderation_check(text: str, banned_words: List[str] = None) -> List[str]:
    """
    Check the input text for banned words and return a list of matches.

    Args:
        text (str): The text to check.
        banned_words (List[str], optional): Custom list of banned words. Defaults to DEFAULT_BANNED.

    Returns:
        List[str]: List of banned words found in the text.
    """
    banned = banned_words or DEFAULT_BANNED
    matches = []
    lowered = text.lower()

    for word in banned:
        # word boundary check
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            matches.append(word)

    return matches
