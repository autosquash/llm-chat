import unittest
from typing import Mapping, TypeGuard

from src.models.placeholders import (
    Placeholder,
    QueryBuildException,
    build_queries,
)

Substitutions = dict[Placeholder, str]


def as_substitutions(d: Mapping[str, str]) -> Substitutions:
    assert is_substitutions_dict(d)
    return d


def is_substitutions_dict(d: Mapping[str, str]) -> TypeGuard[Substitutions]:
    return all(
        placeholder.startswith("{") and placeholder.endswith("}") for placeholder in d
    )


class TestBuildqueries(unittest.TestCase):
    """The format of the placeholders is irrelevant here"""

    def test_build_queries_no_placeholders(self) -> None:
        substitutions = as_substitutions({})
        expected = ["hello"]
        self.assertEqual(
            build_queries("hello", substitutions),
            expected,
        )

    def test_build_queries_with_placeholders(self) -> None:
        raw_query = "What is the capital of {country}?"
        substitutions = as_substitutions({"{country}": "France"})
        expected = ["What is the capital of France?"]
        self.assertEqual(build_queries(raw_query, substitutions), expected)

    def test_build_queries_with_for_command_with_one_element(self) -> None:
        substitutions = as_substitutions({"{start}": "/for 1", "{end}": "5"})
        expected = ["List numbers from 1 to 5"]
        self.assertEqual(
            build_queries("List numbers from {start} to {end}", substitutions), expected
        )

    def test_build_queries_with_for_command_with_two_elements(self) -> None:
        substitutions = as_substitutions({"{start}": "/for 10,20", "{end}": "50"})
        expected = ["List numbers from 10 to 50", "List numbers from 20 to 50"]
        self.assertEqual(
            build_queries("List numbers from {start} to {end}", substitutions), expected
        )

    def test_build_queries_multiple_for_not_supported(self) -> None:
        substitutions = as_substitutions({"{start}": "/for 1", "{end}": "/for 5"})
        with self.assertRaises(QueryBuildException):
            build_queries("List numbers from {start} to {end}", substitutions)


if __name__ == "__main__":
    unittest.main()
