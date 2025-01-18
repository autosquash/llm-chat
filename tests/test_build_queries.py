import unittest
from dataclasses import dataclass
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


@dataclass
class Case:
    description: str
    substitutions: Substitutions
    raw_query: str
    expected: list[str]


cases = [
    Case(
        description="No placeholders",
        substitutions=as_substitutions({}),
        raw_query="hello",
        expected=["hello"],
    ),
    Case(
        description="With placeholders",
        substitutions=as_substitutions({"{country}": "France"}),
        raw_query="What is the capital of {country}?",
        expected=["What is the capital of France?"],
    ),
    Case(
        description="Using the for command with one element",
        substitutions=as_substitutions({"{start}": "/for 1", "{end}": "5"}),
        raw_query="List numbers from {start} to {end}",
        expected=["List numbers from 1 to 5"],
    ),
    Case(
        description="Using the for command with two elements",
        substitutions=as_substitutions({"{start}": "/for 10,20", "{end}": "50"}),
        raw_query="List numbers from {start} to {end}",
        expected=["List numbers from 10 to 50", "List numbers from 20 to 50"],
    ),
]


class TestBuildqueries(unittest.TestCase):
    """The format of the placeholders is irrelevant here"""

    def test_build_queries(self) -> None:
        for case in cases:
            self.assertEqual(
                build_queries(case.raw_query, case.substitutions),
                case.expected,
                case.description,
            )

    def test_build_queries_multiple_for_not_supported(self) -> None:
        substitutions = as_substitutions({"{start}": "/for 1", "{end}": "/for 5"})
        with self.assertRaises(QueryBuildException):
            build_queries("List numbers from {start} to {end}", substitutions)


if __name__ == "__main__":
    unittest.main()
