from typing import Any

import rich_argparse._lazy_rich as r
from rich import get_console
from rich_argparse.contrib import ParagraphRichHelpFormatter
from typing_extensions import override

MAX_WIDTH = 100
MIN_WIDTH = 40


class ReadableColorFormatter(ParagraphRichHelpFormatter):
    """
    A formatter for `argparse` that colorizes with `rich_argparse` and makes a
    few other small changes to improve readability.

    - Wraps text to console width but with a max width of 100 characters, which
      is better for readability in both wide and narrow consoles.
    - Preserves paragraphs, unlike the default argparse formatters.
    - Adds a newline after each action for better readability.
    """

    # TODO: Also improve this so the add_parser() method automatically uses this
    # formatter_class=ReadableColorFormatter.

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        width = max(MIN_WIDTH, min(MAX_WIDTH, get_console().width))
        super().__init__(*args, width=width, **kwargs)

    # This is a bit of a hack but lets us control formatting.
    # Define our own _Section class that inherits from the parent's _Section.
    # This is only   to slightly adjust the layout, in particular to add a newline
    # after each action for better readability.
    class _Section(ParagraphRichHelpFormatter._Section):  # pyright: ignore[reportPrivateUsage]
        @override
        def _render_actions(self, console: r.Console, options: r.ConsoleOptions) -> r.RenderResult:
            if not self.rich_actions:
                return
            options = options.update(no_wrap=True, overflow="ignore")
            help_pos = min(self.formatter._action_max_length + 2, self.formatter._max_help_position)
            help_width = max(self.formatter._width - help_pos, 11)
            indent = r.Text(" " * help_pos)
            # New variables for our feature
            new_line = r.Segment.line()
            num_actions = len(self.rich_actions)

            # Use enumerate to get the index
            for i, (action_header, action_help) in enumerate(self.rich_actions):
                if not action_help:
                    # no help, yield the header and finish
                    yield from console.render(action_header, options)
                    # We remove the 'continue' to allow adding newlines after each item
                else:
                    action_help_lines = self.formatter._rich_split_lines(action_help, help_width)  # pyright: ignore[reportPrivateUsage]
                    if len(action_header) > help_pos - 2:
                        # the header is too long, put it on its own line
                        yield from console.render(action_header, options)
                        action_header = indent
                    action_header.set_length(help_pos)
                    action_help_lines[0].rstrip()
                    yield from console.render(action_header + action_help_lines[0], options)
                    for line in action_help_lines[1:]:
                        line.rstrip()
                        yield from console.render(indent + line, options)

                # Here's our only functional change - add newline if not the last item
                if i < num_actions - 1:
                    yield new_line

            yield ""
