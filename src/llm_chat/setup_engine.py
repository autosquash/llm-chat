from collections.abc import Sequence

from llm_chat.python_modules.FileSystemWrapper.file_manager import FileManager

from llm_chat.command_handler import CommandHandler
from llm_chat.controllers.command_interpreter import CommandInterpreter
from llm_chat.controllers.select_model import SelectModelController
from llm_chat.domain import Model
from llm_chat.engine import MainEngine
from llm_chat.infrastructure.chat_repository.repository import ChatRepository
from llm_chat.infrastructure.main_path_provider import get_main_directory
from llm_chat.infrastructure.now import TimeManager
from llm_chat.llm_manager import LLM_Manager
from llm_chat.model_manager import ModelManager
from llm_chat.protocols import ClientWrapperProtocol
from llm_chat.view.view import View


def setup_engine(
    models: Sequence[Model], client_wrapper: ClientWrapperProtocol
) -> MainEngine:
    """Returns a default MainEngine"""
    select_model_controler = SelectModelController(models)
    chat_repository = ChatRepository(
        get_main_directory(),
        file_manager=FileManager(),
        time_manager=TimeManager(),
    )
    view = View(TimeManager())
    command_interpreter = CommandInterpreter()
    model_manager = ModelManager(client_wrapper)
    llm_manager = LLM_Manager(chat_repository, model_manager)
    command_handler = CommandHandler(
        view=view,
        select_model_controler=select_model_controler,
        llm_manager=llm_manager,
    )
    return MainEngine(models, command_interpreter, command_handler, view)
