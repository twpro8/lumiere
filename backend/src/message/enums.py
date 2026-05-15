from enum import Enum


class MessageType(str, Enum):
    CHAT = "chat"
    CHANNEL = "channel"
