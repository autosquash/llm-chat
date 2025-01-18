from src.domain import CompleteMessage
from src.llm_manager import LLM_Manager
from src.protocols import ViewProtocol

from .controllers import Controllers
from .conversation_loader import ConversationLoader
from .extras import DataChecker, QueriesNumberChecker
from .final_query_extractor import FinalQueryExtractor
from .query_answerer import QueryAnswerer
from .select_model import SelectModelController


def build_controllers(
    select_model_controler: SelectModelController,
    view: ViewProtocol,
    llm_manager: LLM_Manager,
    prev_messages: list[CompleteMessage],
) -> Controllers:
    conversation_loader = ConversationLoader(
        view=view,
        llm_manager=llm_manager,
        prev_messages=prev_messages,
    )
    query_answerer = QueryAnswerer(
        view=view,
        llm_manager=llm_manager,
        prev_messages=prev_messages,
    )
    final_query_extractor = FinalQueryExtractor(view=view)
    return Controllers(
        select_model_controler=select_model_controler,
        conversation_loader=conversation_loader,
        query_answerer=query_answerer,
        final_query_extractor=final_query_extractor,
        data_checker=DataChecker(llm_manager.repository),
        queries_checker=QueriesNumberChecker(view),
    )
