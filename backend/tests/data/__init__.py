"""
Test data.
"""

from pathlib import Path

from tests.utils import read_json

BASE_DIR = Path(__file__).resolve().parent

users = read_json(BASE_DIR / "users.json")
# guilds = read_json(BASE_DIR / "guilds.json")
# channels = read_json(BASE_DIR / "channels.json")
# chats = read_json(BASE_DIR / "chats.json")
# messages = read_json(BASE_DIR / "messages.json")

__all__ = [
    "users",
    # "guilds",
    # "channels",
    # "chats",
    # "messages",
]
