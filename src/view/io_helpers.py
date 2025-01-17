import time
from typing import NewType

import rich

from .string_types import EscapedStr, Raw, StyledStr

StyleTag = NewType("StyleTag", str)

ERROR = StyleTag("[bright_red]")
HIGHLIGHT_ROLE = StyleTag("[light_green]")
NEUTRAL_MSG = StyleTag("[bright_cyan]")
BOLD_STYLE = StyleTag("[blue_violet]")


def escape_for_rich(raw: Raw) -> EscapedStr:
    """
    Escape square brackets in order to print them and their content when using rich.
    It receive a not escaped text to prevent already escaped texts from being escaped again (which would add unwanted backslashes).
    """
    return EscapedStr(raw.value.replace("[", r"\["))


def to_styled(s: str) -> StyledStr:
    """Creates a styled string from a normal string. Equivalent to applying a cast."""
    return StyledStr(EscapedStr(s))


def ensure_escaped(s: Raw | EscapedStr) -> EscapedStr:
    return escape_for_rich(s) if isinstance(s, Raw) else s


def end_style_tag(s: StyleTag) -> str:
    """Create a end tag"""
    assert s[0] == "["
    assert s[-1] == "]"
    return f"[/{s[1:-1]}]"


class SimpleView:
    def print(self, texto: EscapedStr) -> None:
        rich.print(texto)

    def get_input(self, text: EscapedStr | Raw | None = None) -> str:
        """Prompts the user to provide an input, in a styled way"""

        if isinstance(text, Raw):
            text = escape_for_rich(text)
        text_with_breakline_before = f"\n{text}" if text else ""
        rich.print(
            NEUTRAL_MSG + f"{text_with_breakline_before}\n> ",
            end="",
        )
        return input()


def show_error_msg(text: EscapedStr | Raw) -> None:
    """Displays an error message with the given text and make a short pause before returning"""
    text = ensure_escaped(text)
    rich.print(ERROR + f"\n" + text)
    time.sleep(1)


def apply_style_tag(text: EscapedStr | Raw, tag: StyleTag) -> StyledStr:
    assert tag.startswith("[")
    assert tag.endswith("]")
    text = ensure_escaped(text)
    return to_styled(tag + text + end_style_tag(tag))


def highlight_role(role_string: Raw) -> str:
    role_string_str = ensure_escaped(role_string)
    return HIGHLIGHT_ROLE + role_string_str + end_style_tag(HIGHLIGHT_ROLE)


def display_neutral_msg(text: Raw | EscapedStr) -> None:
    text = ensure_escaped(text)
    rich.print(NEUTRAL_MSG + text)
