from __future__ import annotations

from typing import Final, Sequence

from src.domain import CompleteMessage, QueryResult
from src.llm_manager import LLM_Manager
from src.models.placeholders import QueryText
from src.protocols import ViewProtocol
from src.view import Raw


class QueryAnswerer:
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

    def answer_queries(self, queries: Sequence[QueryText], debug: bool = False) -> None:
        """If there are multiple queries, the conversation ends after executing them."""
        assert queries
        messages = None
        for i, query in enumerate(queries):
            messages = self._answer_query(debug, i + 1, len(queries), query)
        self._llm_manager.prev_messages[:] = messages or []

    def _answer_query(
        self, debug: bool, current: int, total: int, query: QueryText
    ) -> list[CompleteMessage] | None:
        self._view.display_processing_query_text(current=current, total=total)
        query_result = self._get_simple_response_from_model(query, debug)
        self._print_interaction(query, query_result)
        self._llm_manager.repository.save_messages(query_result.messages)
        return query_result.messages if current == 1 else None

    def _get_simple_response_from_model(
        self, query: QueryText, debug: bool = False
    ) -> QueryResult:
        return self._llm_manager.model_manager.get_simple_response(
            query, self._llm_manager.prev_messages, debug=debug
        )

    def _print_interaction(self, query: QueryText, query_result: QueryResult) -> None:
        model = self._llm_manager.model_manager.model_wrapper.model
        assert model
        self._view.print_interaction(
            model.model_name,
            Raw(query),
            Raw(query_result.content),
        )
