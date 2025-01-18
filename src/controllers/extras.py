from dataclasses import dataclass
from typing import Final

from src.llm_manager import LLM_Manager
from src.protocols import ViewProtocol
from src.settings import QUERY_NUMBER_LIMIT_WARNING
from src.view.io_helpers import escape_for_rich
from src.view.string_types import Raw


class DataChecker:
    __slots__ = ("_llm_manager", "_view")

    _view: Final[ViewProtocol]
    _llm_manager: Final[LLM_Manager]

    def __init__(self, view: ViewProtocol, llm_manager: LLM_Manager):
        self._view = view
        self._llm_manager = llm_manager

    def check_data(self) -> None:
        ids = self._llm_manager.repository.get_conversation_ids()
        self._view.simple_view.print(escape_for_rich(Raw(f"{len(ids)=}")))
        for id_ in ids:
            try:
                self._llm_manager.repository.load_conversation(id_)
            except Exception as err:
                print(type(err))
                print(err)
                raise


@dataclass(frozen=True)
class QueriesNumberChecker:
    _view: ViewProtocol

    def should_cancel_for_being_too_many_queries(self, number_of_queries: int) -> bool:
        return (
            number_of_queries > QUERY_NUMBER_LIMIT_WARNING
            and not self._view.confirm_launching_many_queries(number_of_queries)
        )
