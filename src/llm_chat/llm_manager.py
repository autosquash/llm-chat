from typing import Final

from llm_chat.domain import CompleteMessage, ModelName, QueryResult
from llm_chat.model_manager import ModelManager
from llm_chat.models.placeholders import QueryText
from llm_chat.protocols import ChatRepositoryProtocol


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

    def get_simple_response(self, query: QueryText, debug: bool = False) -> QueryResult:
        query_result = self.model_manager.get_simple_response(
            query, self.prev_messages, debug=debug
        )
        self.repository.save_messages(query_result.messages)
        return query_result

    def get_model_name(self) -> ModelName | None:
        model = self.model_manager.model_wrapper.model
        if not model:
            return None
        return model.model_name
