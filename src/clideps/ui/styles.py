from rich import get_console, reconfigure

# No emojis on legacy windows.
# This resets to default rich styling, but it's only for legacy windows.
is_legacy_windows = get_console().options.legacy_windows
if is_legacy_windows:
    reconfigure(emoji=False)


def safe_emoji(emoji: str, fallback: str = "") -> str:
    return emoji if not is_legacy_windows else fallback


EMOJI_INFO = safe_emoji("⊘", "[-]")
EMOJI_WARN = safe_emoji("∆", "[!]")
EMOJI_ERROR = safe_emoji("‼︎", "[!!]")
EMOJI_SUCCESS = safe_emoji("✔︎", "(+)")
EMOJI_FAILURE = safe_emoji("✘", "(x)")
EMOJI_CMD = safe_emoji("➤", ">")


STYLE_HEADING = "bold bright_green"
STYLE_HINT = "italic bright_black"
STYLE_EMPH = "bright_green"
STYLE_KEY = "bold bright_blue"
STYLE_CODE = "bold bright_cyan"

STYLE_INFO = "bright_black"
STYLE_WARNING = "bold yellow"
STYLE_ERROR = "bold red"
STYLE_SUCCESS = "bold green"
STYLE_FAILURE = "bold red"
