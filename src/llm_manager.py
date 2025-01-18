from dataclasses import dataclass

from src.model_manager import ModelManager
from src.protocols import ChatRepositoryProtocol


@dataclass
class LLM_Manager:
    repository: ChatRepositoryProtocol
    model_manager: ModelManager
