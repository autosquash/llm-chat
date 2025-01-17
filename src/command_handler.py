from typing import Final

from src.llm_manager import LLM_Manager

from .controllers import (
    Action,
    ActionType,
    Controllers,
    SelectModelController,
    build_controllers,
)
from .protocols import ViewProtocol
from .serde import convert_digits_to_conversation_id
from .strategies import (
    ActionStrategy,
    EstablishSystemPromptAction,
    ShowModelAction,
)
from .view import Raw

PRESS_ENTER_TO_CONTINUE = Raw("Pulsa Enter para continuar")


class ExitException(Exception): ...


class CommandHandler:
    __slots__ = (
        "_view",
        "_controllers",
        "_llm_manager",
    )

    _view: Final[ViewProtocol]
    _controllers: Final[Controllers]
    _llm_manager: Final[LLM_Manager]

    def __init__(
        self,
        *,
        view: ViewProtocol,
        select_model_controler: SelectModelController,
        llm_manager: LLM_Manager,
    ):
        self._view = view
        self._llm_manager = llm_manager
        self._controllers = build_controllers(
            select_model_controler,
            self._view,
            self._llm_manager,
        )

    def prompt_to_select_model(self) -> None:
        model = self._controllers.select_model_controler.select_model()
        self._llm_manager.model_manager.model_wrapper.change(model)

    def process_action(self, action: Action, remaining_input: str) -> None:
        debug = False
        new_conversation = False
        conversation_to_load = None

        action_strategy = self._get_strategy(action)
        if action_strategy:
            action_strategy.execute(remaining_input)
            return

        if action.type == ActionType.EXIT:
            raise ExitException()
        elif action.type == ActionType.HELP:
            self._view.show_help()
            self._view.simple_view.get_input(PRESS_ENTER_TO_CONTINUE)
            return
        elif action.type == ActionType.CHANGE_MODEL:
            self.prompt_to_select_model()
            return
        elif action.type == ActionType.DEBUG:
            debug = True
        elif action.type in (ActionType.LOAD_CONVERSATION, ActionType.LOAD_MESSAGES):
            conversation_to_load = convert_digits_to_conversation_id(remaining_input)
            self._controllers.conversation_loader.load_conversation(
                action, conversation_to_load
            )
            return
        elif action.type == ActionType.NEW_CONVERSATION:
            new_conversation = True
        elif action.type == ActionType.CONTINUE_CONVERSATION:
            # TODO: maybe use ActionType.NEW_CONVERSATION when there is no previous messages
            pass
        elif action.type == ActionType.CHECK_DATA:
            self._controllers.data_checker.check_data()

        else:
            raise RuntimeError(f"Unknown action type: {action.type}")

        if not remaining_input:
            return

        queries = self._controllers.final_query_extractor.get_final_queries(
            remaining_input
        )
        if queries is None:
            return

        number_of_queries = len(queries)
        if self._controllers.queries_checker.should_cancel_for_being_too_many_queries(
            number_of_queries
        ):
            return

        if new_conversation:
            self._llm_manager.prev_messages.clear()
        self._controllers.query_answerer.answer_queries(queries, debug)

    def _get_strategy(self, action: Action) -> ActionStrategy | None:
        action_strategy: ActionStrategy | None = None
        if action.type == ActionType.SHOW_MODEL:
            action_strategy = ShowModelAction(
                self._view, self._llm_manager.model_manager.model_wrapper
            )
        elif action.type == ActionType.SYSTEM_PROMPT:
            action_strategy = EstablishSystemPromptAction(
                self._view, self._llm_manager.prev_messages
            )
        return action_strategy
