from unittest.mock import Mock

from src.controllers.query_answerer import QueryAnswerer
from src.domain import CompleteMessage, QueryResult
from src.llm_manager import LLM_Manager
from src.models.placeholders import QueryText
from src.protocols import ViewProtocol
from src.view.string_types import Raw


def test_query_answerer() -> None:
    # arrange
    llm_manager = Mock(spec=LLM_Manager)
    view = Mock(spec=ViewProtocol)
    query_answerer = QueryAnswerer(view=view, llm_manager=llm_manager)
    llm_manager.prev_messages = []

    messages = [
        Mock(spec=CompleteMessage, name="CompleteMessage of user"),
        Mock(spec=CompleteMessage, name="CompleteMessage of assistant"),
    ]
    query_result = QueryResult("answer to a", messages)
    llm_manager.get_simple_response.return_value = query_result
    llm_manager.get_model_name.return_value = "model_name"

    # act
    query_answerer.answer_queries([QueryText("query a")])

    # assert
    assert view.display_processing_query_text.called
    view.display_processing_query_text.assert_called_once_with(current=1, total=1)

    assert llm_manager.get_simple_response.called
    llm_manager.get_simple_response.assert_called_once_with("query a", debug=False)

    assert llm_manager.get_model_name.called
    llm_manager.get_model_name.assert_called_once_with()

    assert view.print_interaction.called
    view.print_interaction.assert_called_once_with(
        "model_name", Raw(value="query a"), Raw(value="answer to a")
    )

    assert llm_manager.prev_messages == messages
