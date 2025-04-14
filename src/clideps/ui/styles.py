from rich import get_console, reconfigure

# No emojis on legacy windows.
is_legacy_windows = get_console().options.legacy_windows
reconfigure(emoji=not is_legacy_windows)


def safe_emoji(emoji: str, fallback: str = "") -> str:
    return emoji if not is_legacy_windows else fallback


EMOJI_WARN = safe_emoji("∆", "[!]")
EMOJI_ERROR = safe_emoji("‼︎", "[!!]")
EMOJI_SUCCESS = safe_emoji("✔︎", "(+)")
EMOJI_FAILURE = safe_emoji("✘", "(x)")
EMOJI_CMD = safe_emoji("➤", ">")


COLOR_SUCCESS = "green"
COLOR_FAILURE = "bright_red"


STYLE_HEADING = "bold bright_green"
STYLE_HINT = "italic bright_black"
STYLE_EMPH = "bright_green"
STYLE_KEY = "bold bright_blue"
STYLE_CODE = "bold bright_cyan"
STYLE_ERROR = "bold red"
STYLE_WARNING = "bold yellow"
STYLE_SUCCESS = "bold green"
