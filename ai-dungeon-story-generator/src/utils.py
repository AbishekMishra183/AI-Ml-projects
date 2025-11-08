import os
from datetime import datetime
from typing import Tuple
import yaml  # moved import to top for best practice

def ensure_dir(path: str):
    """Ensure that a directory exists; create it if it doesn't."""
    os.makedirs(path, exist_ok=True)

def save_story_file(
    prompt: str,
    continuation: str,
    genre: str,
    folder: str = "stories"
) -> str:
    """
    Save a generated story to a timestamped text file.

    Args:
        prompt (str): Original story prompt.
        continuation (str): Generated continuation.
        genre (str): Story genre.
        folder (str, optional): Folder to save the story. Defaults to "stories".

    Returns:
        str: Full path to the saved file.
    """
    ensure_dir(folder)
    safe_gen = genre.replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"story_{safe_gen}_{ts}.txt"
    fullpath = os.path.join(folder, fname)

    with open(fullpath, "w", encoding="utf-8") as f:
        f.write(f"Prompt:\n{prompt}\n\n---\n\nGenre: {genre}\n\n{continuation}")

    return fullpath

def read_config(path: str) -> Tuple[dict, bool]:
    """
    Read a YAML configuration file.

    Args:
        path (str): Path to the YAML file.

    Returns:
        Tuple[dict, bool]: Loaded configuration and a flag indicating success.
    """
    if not os.path.exists(path):
        return {}, False

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config, True
