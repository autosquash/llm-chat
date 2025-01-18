from typing import Final

from src.domain import CompleteMessage
from src.model_manager import ModelManager
from src.protocols import ChatRepositoryProtocol


class LLM_Manager:
    __slots__ = ("repository", "model_manager", "prev_messages")

    repository: Final[ChatRepositoryProtocol]
    model_manager: Final[ModelManager]
    prev_messages: Final[list[CompleteMessage]]

    def __init__(
        self,
        repository: ChatRepositoryProtocol,
        model_manager: ModelManager,
        *,
        prev_messages: list[CompleteMessage] | None = None,
    ):
        self.repository = repository
        self.model_manager = model_manager
        self.prev_messages = prev_messages if prev_messages is not None else []
