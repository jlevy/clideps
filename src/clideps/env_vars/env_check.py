from __future__ import annotations

import threading
from logging import getLogger

from rich import print as rprint
from rich.text import Text

from clideps.env_vars.dotenv_utils import env_var_is_set, load_dotenv_paths
from clideps.env_vars.env_names import EnvName, get_all_common_env_names
from clideps.ui.rich_output import format_success_or_failure, print_heading

log = getLogger(__name__)


_log_api_setup_done = threading.Event()


def check_env_vars(env_vars: list[str] | None = None) -> list[tuple[EnvName, bool]]:
    """
    Checks which of the provided or default API keys are set in the
    environment or .env files.
    """
    if not env_vars:
        env_vars = get_all_common_env_names()

    return [(EnvName(key), env_var_is_set(key)) for key in env_vars]


def warn_if_missing_api_keys(env_vars: list[str]) -> list[str]:
    """
    Logs a warning if any of the specified API keys are not set in the environment.
    """
    missing_apis = [key for key in env_vars if not env_var_is_set(key)]
    if missing_apis:
        log.warning(
            "Missing recommended API keys (%s):\nCheck your .env file or run `clideps env_setup` to set them.",
            ", ".join(missing_apis),
        )

    return missing_apis


def format_dotenv_check() -> Text:
    """
    Formats the status of .env file setup.
    """
    dotenv_paths = load_dotenv_paths(True, True)

    dotenv_status_text = format_success_or_failure(
        value=bool(dotenv_paths),
        true_str=", ".join(str(path) for path in dotenv_paths),
        false_str="No .env files found. Set up your API keys in a .env file.",
    )

    return dotenv_status_text


def format_env_var_check(env_vars: list[str] | None = None, one_line: bool = False) -> Text:
    """
    Formats the status of env variable setup.
    """
    if not env_vars:
        env_vars = get_all_common_env_names()

    api_key_status_texts = [
        format_success_or_failure(is_found, key.display_str(not one_line))
        for key, is_found in check_env_vars(env_vars)
    ]

    sep = " " if one_line else "\n"
    api_keys_found_text = Text(sep).join(api_key_status_texts)

    return api_keys_found_text


def print_env_check(
    recommended_keys: list[str],
    env_vars: list[str] | None = None,
    once: bool = False,
    one_line: bool = False,
) -> None:
    """
    Convenience function to print status of whether all the given API keys
    were found in the environment or .env files.

    As a convenience, you can pass `once=True` and this will only ever log once.
    """
    if once and _log_api_setup_done.is_set():
        return

    print_heading(".env File Check")
    rprint(format_dotenv_check())
    rprint()

    print_heading("Environment Check Results")
    rprint(format_env_var_check(env_vars, one_line=one_line))

    warn_if_missing_api_keys(recommended_keys)

    _log_api_setup_done.set()
