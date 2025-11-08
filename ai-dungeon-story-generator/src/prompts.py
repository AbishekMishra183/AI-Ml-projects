"""Prompt templates and prompt-building utilities."""
from typing import Dict

PROMPT_TEMPLATES: Dict[str, str] = {
    "Fantasy": (
        "You are an expert fantasy storyteller. Continue this scene with "
        "imaginative worldbuilding, vivid sensory details, and a compelling emotional "
        "arc. Keep dialogue natural and show (don't tell).\n\n"
        "Scene: {prompt}\n\nContinue:"
    ),
    "Mystery": (
        "You are a master mystery novelist. Continue this scene with mounting "
        "tension, subtle clues, and a twist or hook at the end. "
        "Be concise and atmospheric.\n\n"
        "Scene: {prompt}\n\nContinue:"
    ),
    "Sci-Fi": (
        "You are a visionary sci-fi author. Continue the scene with "
        "speculative technology, clear stakes, and logical consequences.\n\n"
        "Scene: {prompt}\n\nContinue:"
    ),
    "Horror": (
        "You are a horror storyteller. Build dread and atmosphere. Use "
        "sensory detail and pace the reveals carefully.\n\n"
        "Scene: {prompt}\n\nContinue:"
    ),
    "Open-ended": "{prompt}\n\nContinue:"
}

def build_prompt(user_prompt: str, genre: str = "Open-ended") -> str:
    """Build a prompt string based on the user input and selected genre."""
    template = PROMPT_TEMPLATES.get(genre, PROMPT_TEMPLATES["Open-ended"])
    return template.format(prompt=user_prompt.strip())
