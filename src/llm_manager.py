from src.model_manager import ModelManager
from src.protocols import ChatRepositoryProtocol


class LLM_Manager:
    __slots__ = ("repository", "model_manager")
    repository: ChatRepositoryProtocol
    model_manager: ModelManager

    def __init__(self, repository: ChatRepositoryProtocol, model_manager: ModelManager):
        self.repository = repository
        self.model_manager = model_manager
