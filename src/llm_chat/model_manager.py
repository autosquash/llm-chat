from typing import Final

from llm_chat.domain import CompleteMessage, QueryResult
from llm_chat.models.messages_ops import add_user_query_in_place
from llm_chat.models.model_wrapper import ModelWrapper
from llm_chat.models.placeholders import QueryText
from llm_chat.protocols import ClientWrapperProtocol


class ModelManager:
    """
    Abstracts the communication with the LLM with the possibility of
    change the model.
    """

    def __init__(self, client_wrapper: ClientWrapperProtocol):
        self.model_wrapper: Final = ModelWrapper()
        self.client_wrapper: Final = client_wrapper

    def get_simple_response(
        self,
        query: QueryText,
        complete_messages: list[CompleteMessage],
        *,
        debug: bool = False,
    ) -> QueryResult:
        assert self.model_wrapper.model
        add_user_query_in_place(complete_messages, query)
        return self.client_wrapper.get_simple_response(
            self.model_wrapper.model, complete_messages, debug=debug
        )
