from typing import Final

from src.controllers.command_interpreter import Action, ActionType
from src.domain import CompleteMessage, ConversationId, ConversationText
from src.llm_manager import LLM_Manager
from src.models.shared import extract_chat_messages
from src.protocols import ViewProtocol
from src.serde import deserialize_conversation_text_into_messages
from src.view import Raw


class ConversationLoader:
    __slots__ = (
        "_view",
        "_llm_manager",
        "_prev_messages",
    )
    _view: Final[ViewProtocol]
    _llm_manager: Final[LLM_Manager]
    _prev_messages: Final[list[CompleteMessage]]

    def __init__(
        self,
        *,
        view: ViewProtocol,
        llm_manager: LLM_Manager,
        prev_messages: list[CompleteMessage],
    ):
        self._view = view
        self._llm_manager = llm_manager
        self._prev_messages = prev_messages

    def load_conversation(
        self, action: Action, conversation_id: ConversationId
    ) -> None:
        """Load a conversation based in its id"""
        conversation_text = (
            self._llm_manager.repository.load_conversation_as_conversation_text(
                conversation_id
            )
        )
        self._prev_messages[:] = deserialize_conversation_text_into_messages(
            conversation_text
        )
        self._display_loaded_conversation(action, conversation_id, conversation_text)
        self._view.display_neutral_msg(Raw("La conversacion ha sido cargada"))

    def _display_loaded_conversation(
        self,
        action: Action,
        conversation_id: ConversationId,
        conversation: ConversationText,
    ) -> None:
        assert self._prev_messages
        if action.type == ActionType.LOAD_CONVERSATION:
            self._view.display_conversation(conversation_id, conversation)
        elif action.type == ActionType.LOAD_MESSAGES:
            self._view.display_messages(
                conversation_id,
                extract_chat_messages(self._prev_messages),
            )
        else:
            raise ValueError(action.type)
