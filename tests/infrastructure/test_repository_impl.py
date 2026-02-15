from unittest.mock import Mock

from llm_chat.python_modules.FileSystemWrapper.file_manager_protocol import (
    FileManagerProtocol,
)

from llm_chat.infrastructure.chat_repository.chat_file_detecter import (
    match_chat_file_pattern,
)
from llm_chat.infrastructure.chat_repository.implementer import (
    ChatRepositoryImplementer,
    DataLocation,
)


def test_match_filename() -> None:
    assert match_chat_file_pattern("0033.chat")
    assert not match_chat_file_pattern("33.chat")
    assert not match_chat_file_pattern("033.chat")
    assert not match_chat_file_pattern("00033.chat")
    assert not match_chat_file_pattern("0033.txt")
    assert not match_chat_file_pattern("0033")
    assert not match_chat_file_pattern("hola.chat")


def test_chat_repository_impl_initialization() -> None:
    repository = ChatRepositoryImplementer()
    repository.init(Mock(spec=DataLocation), Mock(spec=FileManagerProtocol))
    assert repository.is_initialized
