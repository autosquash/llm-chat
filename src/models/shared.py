from dataclasses import dataclass
from enum import Enum
from typing import NewType, Sequence

from src.domain import ChatMessage

__all__ = ["ModelName", "Model", "CompleteMessage"]

ModelName = NewType("ModelName", str)


class Platform(Enum):
    Mistral = "Mistral"
    OpenAI = "OpenAI"


@dataclass(frozen=True)
class Model:
    platform: Platform | None
    model_name: ModelName


@dataclass(frozen=True)
class CompleteMessage:
    chat_msg: ChatMessage
    model: Model | None = None


def extract_chat_messages(
    complete_messages: Sequence[CompleteMessage],
) -> list[ChatMessage]:
    return [complete_chat.chat_msg for complete_chat in complete_messages]
