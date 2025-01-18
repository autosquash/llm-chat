from typing import Any, cast
from unittest.mock import Mock

import pytest

from src.controllers.command_interpreter import Action, ActionType
from src.controllers.final_query_extractor import DELIBERATE_INPUT_TIME
from src.domain import (
    CompleteMessage,
    ConversationId,
    ConversationText,
    Model,
    ModelName,
    QueryResult,
)
from src.serde.shared import SCHEMA_VERSION
from src.view import Raw

from tests.command_handler_fixtures import (
    CommandHandlerAdvancedFixture,
    CommandHandlerFixture,
    CommandHandlerFixtureWithModel,
)
from tests.objects import TEXT_1


def test_process_system(command_handler_fixture: CommandHandlerFixture) -> None:
    """
    Tests that system prompts can be processed and the result is added to previous
    messages correctly.
    """
    fixture = command_handler_fixture
    system_prompt = "System prompt string"

    fixture.command_handler.process_action(
        Action(ActionType.SYSTEM_PROMPT), system_prompt
    )

    assert len(fixture.prev_messages_stub) == 1
    first_chat_msg = fixture.prev_messages_stub[0].chat_msg
    assert first_chat_msg.role == "system"
    assert first_chat_msg.content == system_prompt
    fixture.mock_view.write_object.assert_called_once_with("System prompt established")


def test_show_model_works_when_no_extra_chat(
    command_handler_fixture_with_model: CommandHandlerFixtureWithModel,
) -> None:
    """
    Tests that displaying the current model works correctly when no extra chat is present.
    """
    fixture = command_handler_fixture_with_model
    remaining = ""

    fixture.command_handler.process_action(Action(ActionType.SHOW_MODEL), remaining)

    assert len(fixture.prev_messages_stub) == 0
    fixture.mock_view.display_neutral_msg.assert_called_once_with(
        Raw("El modelo actual es model_name_test")
    )


def test_show_model_fails_when_there_is_extra_prompt(
    command_handler_fixture_with_model: CommandHandlerFixtureWithModel,
) -> None:
    """
    Tests that an error is raised when extraneous text is present in the prompt after
    the command to show the model.
    """

    remaining = "some text"

    with pytest.raises(ValueError):
        command_handler_fixture_with_model.command_handler.process_action(
            Action(ActionType.SHOW_MODEL), remaining
        )


def test_chat_with_model(
    command_handler_advanced_fixture: CommandHandlerAdvancedFixture,
) -> None:
    """
    Simulates a conversation with the model, checking the correct continuation of interaction.
    """
    fixture = command_handler_advanced_fixture

    fixture.mock_view.input_extra_line.side_effect = fixture.user_prompt_lines
    fixture.mock_client_wrapper.get_simple_response.side_effect = (
        get_simple_response_stub
    )
    remaining = "hello, how are you?"

    fixture.command_handler.process_action(
        Action(ActionType.CONTINUE_CONVERSATION), remaining
    )
    fixture.mock_view.print_interaction.assert_called()
    print_interaction_calls = fixture.mock_view.print_interaction.mock_calls
    assert len(print_interaction_calls) == 1
    assert len(fixture.prev_messages_stub) == 2


def test_chat_with_model_using_placeholder(
    command_handler_advanced_fixture: CommandHandlerAdvancedFixture,
) -> None:
    """
    Checks that substitutions are made in the user's message, and a model response
    is requested.
    """
    fixture = command_handler_advanced_fixture
    user_substitutions = {"$0something": "anything"}
    fixture.mock_view.input_extra_line.side_effect = fixture.user_prompt_lines
    fixture.mock_view.get_raw_substitutions_from_user.return_value = user_substitutions
    fixture.mock_client_wrapper.get_simple_response.side_effect = (
        get_simple_response_stub
    )
    remaining = "hello, how are you? What is $0something?"
    expected_user_content_replaced = (
        "hello, how are you? What is anything?\nsomething more"
    )

    fixture.command_handler.process_action(
        Action(ActionType.CONTINUE_CONVERSATION), remaining
    )

    fixture.mock_client_wrapper.get_simple_response.assert_called()
    calls = fixture.mock_client_wrapper.get_simple_response.mock_calls
    assert len(calls) == 1
    messages = calls[0].args[1]
    assert len(messages) == 2
    user_message_replaced = messages[0]
    assert user_message_replaced.chat_msg.content == expected_user_content_replaced


def test_chat_with_model_continue(
    command_handler_advanced_fixture: CommandHandlerAdvancedFixture,
) -> None:
    """
    Simulates a conversation with the model, checking the correct continuation of
    interaction (although the model repeats the same thing for simplicity).
    """
    fixture = command_handler_advanced_fixture
    # arrange
    fixture.mock_view.input_extra_line.side_effect = (
        fixture.user_prompt_lines + fixture.user_prompt_lines
    )
    fixture.mock_client_wrapper.get_simple_response.side_effect = (
        get_simple_response_stub
    )
    user_prompt = "hello, how are you?"

    # act
    fixture.command_handler.process_action(
        Action(ActionType.CONTINUE_CONVERSATION), user_prompt
    )
    fixture.command_handler.process_action(
        Action(ActionType.CONTINUE_CONVERSATION), "then, again, how are you?"
    )

    # assert
    fixture.mock_client_wrapper.get_simple_response.assert_called()
    fixture.mock_view.print_interaction.assert_called()
    calls = fixture.mock_view.print_interaction.mock_calls
    assert len(calls) == 2
    assert len(fixture.prev_messages_stub) == 4


def test_show_help_wait_user_press_enter(
    command_handler_fixture: CommandHandlerFixture,
) -> None:
    """
    Tests the help display functionality, requiring the user to press enter to proceed.
    """
    fixture = command_handler_fixture
    remaining = ""

    fixture.command_handler.process_action(Action(ActionType.HELP), remaining)

    assert len(fixture.prev_messages_stub) == 0
    fixture.mock_view.simple_view.get_input.assert_called_once()
    calls = fixture.mock_view.simple_view.get_input.mock_calls
    assert len(calls) == 1
    prompt_for_user = calls[0].args[0]
    assert isinstance(prompt_for_user, Raw)
    assert "enter" in prompt_for_user.value.lower()


def test_debug_command_works(
    command_handler_advanced_fixture: CommandHandlerAdvancedFixture,
) -> None:
    """
    Tests the debug functionality within the model interaction, ensuring the debug flag
    is correctly sent to ClientWrapper instance.
    """
    fixture = command_handler_advanced_fixture
    remaining = "some text"
    fixture.mock_view.input_extra_line.side_effect = fixture.user_prompt_lines
    fixture.mock_client_wrapper.get_simple_response.return_value = QueryResult("", [])

    fixture.command_handler.process_action(Action(ActionType.DEBUG), remaining)

    calls = fixture.mock_client_wrapper.get_simple_response.mock_calls
    assert len(calls) == 1
    assert calls[0].kwargs["debug"] == True


def test_check_command_no_data(command_handler_fixture: CommandHandlerFixture) -> None:
    fixture = command_handler_fixture
    fixture.mock_repository.get_conversation_ids.return_value = []
    fixture.command_handler.process_action(Action(ActionType.CHECK_DATA), "")


def test_check_command_with_right_data(
    command_handler_fixture: CommandHandlerFixture,
) -> None:
    fixture = command_handler_fixture
    fixture.mock_repository.get_conversation_ids.return_value = [ConversationId("01")]
    fixture.command_handler.process_action(Action(ActionType.CHECK_DATA), "")


def test_check_command_with_wrong_data(
    command_handler_fixture: CommandHandlerFixture,
) -> None:
    fixture = command_handler_fixture
    fixture.mock_repository.get_conversation_ids.return_value = [ConversationId("01")]

    def load_conversation(id_: ConversationId) -> ConversationText:
        if id_ == "01":
            raise RuntimeError()
        return ConversationText("", SCHEMA_VERSION)

    fixture.mock_repository.load_conversation = load_conversation
    with pytest.raises(RuntimeError):
        fixture.command_handler.process_action(Action(ActionType.CHECK_DATA), "")


def test_load_conversation(
    command_handler_advanced_fixture: CommandHandlerAdvancedFixture,
) -> None:
    """
    Tests the loading of a specific conversation by ID, checking calls to retrieval
    and display of conversation data.
    """
    fixture = command_handler_advanced_fixture
    remaining = "42"
    fixture.mock_repository.load_conversation_as_conversation_text.return_value = (
        ConversationText(TEXT_1, SCHEMA_VERSION)
    )

    fixture.command_handler.process_action(
        Action(ActionType.LOAD_CONVERSATION), remaining
    )

    fixture.mock_repository.load_conversation_as_conversation_text.assert_called_once()
    fixture.mock_view.display_conversation.assert_called_once()
    calls = fixture.mock_view.display_conversation.mock_calls
    assert calls[0].args[0] == ConversationId("0042")
    fixture.mock_view.display_neutral_msg.assert_called_once_with(
        Raw("La conversacion ha sido cargada")
    )


def get_simple_response_stub(
    _model: Model,
    messages: list[CompleteMessage],
    debug: bool = False,
) -> QueryResult:
    messages.append(Mock(spec=CompleteMessage))
    return QueryResult(
        "",
        messages,
    )


def get_print_interaction_content_arg(call: Any) -> Raw:
    return cast(Raw, call.args[3])


def test_extra_lines_without_delay(
    command_handler_fixture: CommandHandlerFixture,
) -> None:
    # Here RuntimeError is raised because `end` is interpreted as part of a
    # multiline copy-paste
    fixture = command_handler_fixture
    lines = ["do", "  something", "end", "more"]

    def input_extra_line() -> tuple[str, float]:
        if lines:
            return (lines.pop(0), 0)
        raise RuntimeError

    model_name = ModelName("model_name_test")
    model = Model(None, model_name)

    fixture.command_handler._llm_manager.model_manager.model_wrapper.change(  # pyright: ignore [reportPrivateUsage]
        model
    )
    fixture.mock_view.input_extra_line = input_extra_line
    fixture.mock_client_wrapper.get_simple_response.side_effect = (
        get_simple_response_stub
    )
    with pytest.raises(RuntimeError):
        fixture.command_handler.process_action(
            Action(ActionType.CONTINUE_CONVERSATION), "something"
        )


def test_extra_lines_with_delay(command_handler_fixture: CommandHandlerFixture) -> None:
    # RuntimeError is not raised because `end` is interpreted as deliberated command
    fixture = command_handler_fixture
    lines = ["second line", "third line", "fourth line", "end"]

    def input_extra_line() -> tuple[str, float]:
        if lines:
            return (lines.pop(), DELIBERATE_INPUT_TIME)
        raise RuntimeError

    model_name = ModelName("model_name_test")
    model = Model(None, model_name)

    fixture.command_handler._llm_manager.model_manager.model_wrapper.change(  # pyright: ignore [reportPrivateUsage]
        model
    )
    fixture.mock_view.input_extra_line = input_extra_line
    fixture.mock_client_wrapper.get_simple_response.side_effect = (
        get_simple_response_stub
    )
    fixture.command_handler.process_action(
        Action(ActionType.CONTINUE_CONVERSATION), "something"
    )
