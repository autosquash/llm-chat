from unittest.mock import Mock

import pytest

from src.command_handler import CommandHandler
from src.controllers.final_query_extractor import DELIBERATE_INPUT_TIME
from src.controllers.select_model import SelectModelController
from src.domain import CompleteMessage, Model, ModelName
from src.infrastructure.llm_connection import ClientWrapper
from src.infrastructure.now import TimeManager
from src.llm_manager import LLM_Manager
from src.model_manager import ModelManager
from src.models.model_wrapper import ModelWrapper
from src.protocols import ChatRepositoryProtocol
from src.view.view import View


class CommandHandlerFixture:
    """
    Base class for testing command handlers. This class should not be directly instantiated.
    Therefore it should not include tests.
    """

    def __init__(self) -> None:
        """
        Sets up necessary mock objects and initial state for each test method.
        """
        self.mock_view = Mock(spec=View)
        self.mock_select_model_controler = Mock(spec=SelectModelController)
        self.mock_repository = Mock(spec=ChatRepositoryProtocol)
        self.mock_client_wrapper = Mock(spec=ClientWrapper)
        self.mock_model_wrapper = Mock(spec=ModelWrapper)
        self.prev_messages_stub: list[CompleteMessage] = []
        self.llm_manager = LLM_Manager(
            self.mock_repository,
            ModelManager(self.mock_client_wrapper),
            prev_messages=self.prev_messages_stub,
        )
        self.mock_time_manager = Mock(spec=TimeManager)
        self.mock_time_manager.get_current_time.return_value = "2024-03-01 01:30:00"
        self.command_handler = CommandHandler(
            view=self.mock_view,
            select_model_controler=self.mock_select_model_controler,
            llm_manager=self.llm_manager,
        )


class CommandHandlerFixtureWithModel(CommandHandlerFixture):
    def __init__(self) -> None:
        """
        Sets up additional variables and inherits the base setup, define a multiline
        user prompt to ensure that tests avoid infinite loops in mutation testing.
        """
        super().__init__()
        self._select_model()

    def _select_model(self) -> None:
        """
        Private helper method for selecting a model using the SelectModelController mock.
        """
        model_name = ModelName("Model name test")
        self.mock_select_model_controler.select_model.return_value = Model(
            None, model_name
        )
        self.command_handler.prompt_to_select_model()


class CommandHandlerAdvancedFixture(CommandHandlerFixtureWithModel):
    def __init__(self) -> None:
        """
        In addition to inherited behavior, define a multiline
        user prompt to ensure that tests avoid infinite loops in mutation testing.
        """
        super().__init__()
        # if a line is not sent before the `end` command, there is a risk
        # of creating an infinite loop when running the mutation tests
        self.user_prompt_lines = [
            (line, DELIBERATE_INPUT_TIME) for line in ["something more", "end"]
        ]


@pytest.fixture
def command_handler_fixture() -> CommandHandlerFixture:
    return CommandHandlerFixture()


@pytest.fixture
def command_handler_fixture_with_model() -> CommandHandlerFixtureWithModel:
    return CommandHandlerFixtureWithModel()


@pytest.fixture
def command_handler_advanced_fixture() -> CommandHandlerAdvancedFixture:
    return CommandHandlerAdvancedFixture()
