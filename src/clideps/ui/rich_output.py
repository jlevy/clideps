from typing import Literal, TypeAlias

from flowmark import fill_text
from rich import get_console
from rich.text import Text

from clideps.ui.styles import (
    EMOJI_ERROR,
    EMOJI_FAILURE,
    EMOJI_INFO,
    EMOJI_SUCCESS,
    EMOJI_WARN,
    STYLE_ERROR,
    STYLE_FAILURE,
    STYLE_HEADING,
    STYLE_HINT,
    STYLE_INFO,
    STYLE_KEY,
    STYLE_SUCCESS,
    STYLE_WARNING,
)

console = get_console()

rprint = console.print


def print_heading(message: str) -> None:
    rprint()
    rprint(Text(message, style=STYLE_HEADING))


def print_subtle(message: str) -> None:
    rprint(Text(message, style=STYLE_HINT))


def print_success(message: str) -> None:
    rprint()
    rprint(Text(f"{EMOJI_SUCCESS} {message}", style=STYLE_SUCCESS))


def print_status(message: str) -> None:
    rprint()
    rprint(Text(message, style=STYLE_WARNING))


def print_warning(message: str) -> None:
    rprint()
    rprint(Text(f"{EMOJI_WARN} Warning: {message}", style=STYLE_WARNING))


def print_error(message: str) -> None:
    rprint()
    rprint(Text(f"{EMOJI_ERROR} Error: {message}", style=STYLE_ERROR))


def print_cancelled() -> None:
    print_warning("Operation cancelled.")


def print_failed(e: Exception) -> None:
    print_error(f"Failed to create project: {e}")


Status: TypeAlias = bool | Literal["info", "warning", "error"]


def status_emoji(value: Status, success_only: bool = False) -> str:
    if value is True:
        return EMOJI_SUCCESS
    elif value is False:
        return " " if success_only else EMOJI_FAILURE
    elif value == "info":
        return EMOJI_INFO
    elif value == "warning":
        return EMOJI_WARN
    elif value == "error":
        return EMOJI_ERROR
    else:
        raise ValueError(f"Invalid status: {value}")


def format_status_emoji(status: Status, success_only: bool = False) -> Text:
    if status is True:
        style = STYLE_SUCCESS
    elif status is False:
        style = STYLE_FAILURE
    elif status == "info":
        style = STYLE_INFO
    elif status == "warning":
        style = STYLE_WARNING
    elif status == "error":
        style = STYLE_ERROR
    else:
        raise ValueError(f"Invalid status: {status}")

    return Text(status_emoji(status, success_only), style=style)


def format_success(message: str | Text) -> Text:
    return Text.assemble(format_status_emoji(True), message)


def format_failure(message: str | Text) -> Text:
    return Text.assemble(format_status_emoji(False), message)


def format_status(status: Status, message: str | Text, space: str = "") -> Text:
    return Text.assemble(format_status_emoji(status), space, message)


def format_success_or_failure(
    value: bool, true_str: str | Text = "", false_str: str | Text = "", space: str = ""
) -> Text:
    """
    Format a success or failure message with an emoji followed by the true or false
    string. If false_str is not provided, it will be the same as true_str.
    """
    emoji = format_status_emoji(value)
    if true_str or false_str:
        return Text.assemble(emoji, space, true_str if value else (false_str or true_str))
    else:
        return emoji


def format_name_and_value(
    name: str | Text,
    doc: str,
    extra_note: str | None = None,
    extra_indent: str = "",
) -> Text:
    """
    Format a key value followed by a note and a description.
    """
    if isinstance(name, str):
        name = Text(name, style=STYLE_KEY)
    doc = fill_text(
        doc, initial_column=len(name) + 2 + len(extra_indent), extra_indent=extra_indent
    )

    return Text.assemble(
        extra_indent,
        name,
        ((" " + extra_note, STYLE_HINT) if extra_note else ""),
        (": ", STYLE_HINT),
        doc,
    )
