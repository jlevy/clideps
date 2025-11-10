from __future__ import annotations

from collections.abc import Callable
from typing import Any

import rich_argparse._lazy_rich as r
from rich import get_console
from rich.markdown import Markdown
from rich_argparse.contrib import ParagraphRichHelpFormatter
from typing_extensions import override


def get_readable_console_width(min_width: int = 40, max_width: int = 100) -> int:
    """
    Get a readable console width by default between 40 and 100 characters.
    Very wide consoles are common but not readable for long text.
    """
    return max(min_width, min(max_width, get_console().width))


def default_text_wrapper(text: str, as_markdown: bool = False) -> str | Markdown:
    """
    Default wrapper for text formatting.

    If as_markdown is True, returns a Rich Markdown object that rich_argparse will
    render with full styling (bold, lists, code blocks, etc.). Rich handles its own
    width management for Markdown objects, so this bypasses the parent formatter's
    wrapping logic.

    If as_markdown is False, returns plain text unchanged, which will then be
    wrapped by the parent formatter according to the configured width.
    """
    if as_markdown:
        return Markdown(text, style="argparse.text")
    return text


class ReadableColorFormatter(ParagraphRichHelpFormatter):
    """
    A formatter for `argparse` that colorizes with `rich_argparse` and makes a
    few other small changes to improve readability.

    - Preserves paragraphs, unlike the default argparse formatters.
    - Wraps text to console width with configurable min and max limits, which
      is better for readability in both wide and narrow consoles.
    - Adds a newline after each action for better readability.
    - Optionally formats descriptions and epilogs as Markdown.

    Args:
        wrap_to_console: If True, wraps text to console width (constrained by
            min_width and max_width). If False, uses the full terminal width.
        max_width: Maximum width for text wrapping when wrap_to_console is True.
        min_width: Minimum width for text wrapping when wrap_to_console is True.
        format_markdown: If True, automatically formats descriptions and epilogs
            as Markdown using Rich's Markdown renderer.
        text_wrapper: Custom function to preprocess text.
            Receives text and as_markdown boolean parameter.
            Returns either plain text string or a Rich renderable (like Markdown).
            Defaults to `default_text_wrapper`.
        add_action_spacing: If True, adds newline between actions for readability.
    """

    def __init__(
        self,
        prog: str,
        *,
        wrap_to_console: bool = True,
        max_width: int = 100,
        min_width: int = 40,
        format_markdown: bool = False,
        text_wrapper: Callable[[str, bool], str | Markdown] | None = None,
        add_action_spacing: bool = True,
        **kwargs: Any,
    ) -> None:
        if wrap_to_console:
            width = max(min_width, min(max_width, get_console().width))
            kwargs.setdefault("width", width)

        super().__init__(prog, **kwargs)
        self.format_markdown: bool = format_markdown
        self.text_wrapper: Callable[[str, bool], str | Markdown] = (
            text_wrapper or default_text_wrapper
        )
        self.add_action_spacing: bool = add_action_spacing

    @override
    def add_text(self, text: Any) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Override to support markdown formatting when enabled.

        When format_markdown is True, we intercept text descriptions/epilogs before
        they reach the parent formatter. We convert them to Rich Markdown objects
        and use add_renderable() instead of add_text(). This allows rich_argparse
        to render them with full markdown styling (bold, lists, code blocks, etc.).

        Note: We need the pyright ignore because rich_argparse's add_text() accepts
        RenderableType | None, but we want to accept str to process it first.
        """
        if text and isinstance(text, str) and self.format_markdown:
            result = self.text_wrapper(text, True)
            if not isinstance(result, str):
                # Got a Rich renderable (like Markdown) - use add_renderable
                # so rich_argparse renders it directly with styling
                self.add_renderable(result)
                return
        super().add_text(text)

    class _Section(ParagraphRichHelpFormatter._Section):  # pyright: ignore[reportPrivateUsage]
        """
        Custom section renderer for better action formatting.

        We override _render_actions to add optional spacing between actions (like
        subcommands or arguments). This makes help text more scannable by adding
        visual separation between items.

        Note: We need pyright ignore for accessing _Section which is technically
        private, but this is the standard way to customize rich_argparse formatting.
        """

        @override
        def _render_actions(self, console: r.Console, options: r.ConsoleOptions) -> r.RenderResult:
            if not self.rich_actions:
                return
            options = options.update(no_wrap=True, overflow="ignore")
            help_pos = min(self.formatter._action_max_length + 2, self.formatter._max_help_position)
            help_width = max(self.formatter._width - help_pos, 11)
            indent = r.Text(" " * help_pos)
            new_line = r.Segment.line()
            num_actions = len(self.rich_actions)

            for i, (action_header, action_help) in enumerate(self.rich_actions):
                if not action_help:
                    yield from console.render(action_header, options)
                else:
                    action_help_lines = self.formatter._rich_split_lines(action_help, help_width)  # pyright: ignore[reportPrivateUsage]
                    if len(action_header) > help_pos - 2:
                        # Header is too long, put it on its own line
                        yield from console.render(action_header, options)
                        action_header = indent
                    action_header.set_length(help_pos)
                    action_help_lines[0].rstrip()
                    yield from console.render(action_header + action_help_lines[0], options)
                    for line in action_help_lines[1:]:
                        line.rstrip()
                        yield from console.render(indent + line, options)

                # Add spacing between actions if configured (and not last item)
                # Access the parent formatter to check the add_action_spacing setting
                formatter = self.formatter
                assert isinstance(formatter, ReadableColorFormatter)
                if formatter.add_action_spacing and i < num_actions - 1:
                    yield new_line

            yield ""
