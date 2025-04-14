from flowmark import fill_text
from rich import get_console
from rich.text import Text

from clideps.ui.styles import (
    COLOR_FAILURE,
    COLOR_SUCCESS,
    EMOJI_ERROR,
    EMOJI_FAILURE,
    EMOJI_SUCCESS,
    EMOJI_WARN,
    STYLE_ERROR,
    STYLE_HEADING,
    STYLE_HINT,
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


def success_emoji(value: bool, success_only: bool = False) -> str:
    return EMOJI_SUCCESS if value else " " if success_only else EMOJI_FAILURE


def format_success_emoji(value: bool, success_only: bool = False) -> Text:
    return Text(success_emoji(value, success_only), style=COLOR_SUCCESS if value else COLOR_FAILURE)


def format_success(message: str | Text) -> Text:
    return Text.assemble(format_success_emoji(True), message)


def format_failure(message: str | Text) -> Text:
    return Text.assemble(format_success_emoji(False), message)


def format_success_or_failure(
    value: bool, true_str: str | Text = "", false_str: str | Text = "", space: str = ""
) -> Text:
    """
    Format a success or failure message with an emoji followed by the true or false
    string. If false_str is not provided, it will be the same as true_str.
    """
    emoji = format_success_emoji(value)
    if true_str or false_str:
        return Text.assemble(emoji, space, true_str if value else (false_str or true_str))
    else:
        return emoji


def format_name_and_value(
    name: str | Text,
    doc: str,
    extra_note: str | None = None,
) -> Text:
    """
    Format a key value followed by a note and a description.
    """
    if isinstance(name, str):
        name = Text(name, style=STYLE_KEY)
    doc = fill_text(doc, initial_column=len(name) + 2)

    return Text.assemble(
        name,
        ((" " + extra_note, STYLE_HINT) if extra_note else ""),
        (": ", STYLE_HINT),
        doc,
    )
