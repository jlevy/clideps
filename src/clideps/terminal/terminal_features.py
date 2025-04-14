import os
from dataclasses import dataclass

from rich import get_console
from rich.text import Text

from clideps.terminal.osc_utils import osc8_link_rich, terminal_supports_osc8
from clideps.terminal.terminal_images import terminal_supports_sixel
from clideps.ui.rich_output import format_success_or_failure


@dataclass(frozen=True)
class TerminalInfo:
    term: str
    term_program: str
    terminal_width: int
    supports_sixel: bool
    supports_osc8: bool

    @property
    def name_str(self) -> str:
        return f"{self.term} ({self.term_program})"

    def formatted_details(self) -> Text:
        return Text.assemble(
            f"{self.terminal_width} cols, ",
            format_success_or_failure(
                self.supports_sixel, true_str="Sixel images", false_str="No Sixel images"
            ),
            ", ",
            format_success_or_failure(
                self.supports_osc8,
                true_str=osc8_link_rich(
                    "https://github.com/Alhadis/OSC8-Adoption", "OSC 8 hyperlinks"
                ),
                false_str="No OSC 8 hyperlinks",
            ),
        )

    def formatted(self) -> Text:
        return Text.assemble(
            f"Terminal is {self.name_str}, ",
            self.formatted_details(),
        )


def terminal_check() -> TerminalInfo:
    """
    Get a summary of the current terminal's name, settings, and capabilities.
    """
    return TerminalInfo(
        term=os.environ.get("TERM", ""),
        term_program=os.environ.get("TERM_PROGRAM", ""),
        supports_sixel=terminal_supports_sixel(),
        supports_osc8=terminal_supports_osc8(),
        terminal_width=get_console().width,
    )
