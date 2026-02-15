from typing import Final

from llm_chat.controllers.command_interpreter import Action, ActionType
from llm_chat.domain import ConversationId, ConversationText
from llm_chat.llm_manager import LLM_Manager
from llm_chat.models.shared import extract_chat_messages
from llm_chat.protocols import ViewProtocol
from llm_chat.serde import deserialize_conversation_text_into_messages
from llm_chat.view import Raw


class ConversationLoader:
    __slots__ = (
        "_view",
        "_llm_manager",
    )
    _view: Final[ViewProtocol]
    _llm_manager: Final[LLM_Manager]

    def __init__(
        self,
        *,
        view: ViewProtocol,
        llm_manager: LLM_Manager,
    ):
        self._view = view
        self._llm_manager = llm_manager

    def load_conversation(
        self, action: Action, conversation_id: ConversationId
    ) -> None:
        """Load a conversation based in its id"""
        conversation_text = (
            self._llm_manager.repository.load_conversation_as_conversation_text(
                conversation_id
            )
        )
        self._llm_manager.prev_messages[:] = (
            deserialize_conversation_text_into_messages(conversation_text)
        )
        self._display_loaded_conversation(action, conversation_id, conversation_text)
        self._view.display_neutral_msg(Raw("La conversacion ha sido cargada"))

    def _display_loaded_conversation(
        self,
        action: Action,
        conversation_id: ConversationId,
        conversation: ConversationText,
    ) -> None:
        assert self._llm_manager.prev_messages
        if action.type == ActionType.LOAD_CONVERSATION:
            self._view.display_conversation(conversation_id, conversation)
        elif action.type == ActionType.LOAD_MESSAGES:
            self._view.display_messages(
                conversation_id,
                extract_chat_messages(self._llm_manager.prev_messages),
            )
        else:
            raise ValueError(action.type)
