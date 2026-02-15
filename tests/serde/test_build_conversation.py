import unittest

from llm_chat.domain import ConversationId
from llm_chat.serde import convert_digits_to_conversation_id, serialize_conversation

from tests.objects import serialization_example_01


class TestCreateConversationTexts(unittest.TestCase):

    def test_create_conversation_texts(self) -> None:
        example = serialization_example_01
        expected_conversation_text = example.serialized_text
        result = serialize_conversation(
            example.complete_messages,
            ConversationId("0001"),
            "2024-03-16 14:50:15",
        )
        self.assertEqual(expected_conversation_text, result)

    def test_convert_digits_to_conversation_id(self) -> None:
        conversation_id = convert_digits_to_conversation_id("1")
        self.assertEqual(ConversationId("0001"), conversation_id)

    def test_convert_digits_to_conversation_id_wrong(self) -> None:
        """Too much digits"""
        with self.assertRaises(ValueError):
            convert_digits_to_conversation_id("11111")


if __name__ == "__main__":
    unittest.main()
