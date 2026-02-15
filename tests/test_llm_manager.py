# si le pedimos al llm manager que responda una query, grabara los mensajes
from unittest.mock import Mock

from llm_chat.domain import CompleteMessage, QueryResult
from llm_chat.llm_manager import LLM_Manager
from llm_chat.model_manager import ModelManager
from llm_chat.models.placeholders import QueryText
from llm_chat.protocols import ChatRepositoryProtocol


def test_llm_manager() -> None:
    mock_repository = Mock(spec=ChatRepositoryProtocol)
    mock_model_manager = Mock(spec=ModelManager)

    messages = [
        Mock(spec=CompleteMessage, name="CompleteMessage of user"),
        Mock(spec=CompleteMessage, name="CompleteMessage of assistant"),
    ]
    query_result = QueryResult("answer to a", messages)
    mock_model_manager.get_simple_response.return_value = query_result

    llm_manager = LLM_Manager(mock_repository, mock_model_manager)

    llm_manager.get_simple_response(QueryText("query a"))

    assert mock_repository.save_messages.called
    mock_repository.save_messages.assert_called_once_with(messages)
