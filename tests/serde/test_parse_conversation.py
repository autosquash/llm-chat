from llm_chat.domain import (
    ChatMessage,
    ConversationId,
    ConversationText,
    SchemaVersionId,
)
from llm_chat.serde import Conversation, deserialize_conversation_text_into_messages
from llm_chat.serde.deserialize import deserialize_into_conversation_object

from tests.objects import serialization_example_01, serialization_example_02


def create_chat_msg(role: str, content: str) -> ChatMessage:
    return ChatMessage(role=role, content=content)


SCHEMA_VERSION = SchemaVersionId("0.2")
CASES = [
    (
        serialization_example_01.serialized_text,
        Conversation(
            ConversationId("0001"),
            SCHEMA_VERSION,
            4,
            "2024-03-16 14:50:15",
            serialization_example_01.complete_messages,
        ),
    ),
    (
        serialization_example_02.serialized_text,
        Conversation(
            ConversationId("0002"),
            SCHEMA_VERSION,
            2,
            "2023-05-20 13:00:02",
            serialization_example_02.complete_messages,
        ),
    ),
]


def test_deserialize_conversation() -> None:
    for text, expected_conversation in CASES:
        conversation = deserialize_into_conversation_object(
            ConversationText(text, SCHEMA_VERSION),
            preserve_model=True,
            check_model_exists=False,
        )
        assert conversation == expected_conversation


def test_deserialize_messages() -> None:
    for example in [
        serialization_example_01,
        serialization_example_02,
    ]:
        result = deserialize_conversation_text_into_messages(
            ConversationText(example.serialized_text, SCHEMA_VERSION),
            preserve_model=True,
            check_model_exists=False,
        )
        assert result == example.complete_messages
