from __future__ import annotations

import threading
from logging import getLogger

from rich import print as rprint
from rich.console import Group
from rich.text import Text

from clideps.env_vars.common_env_vars import CommonEnvVar, get_all_common_env_vars
from clideps.env_vars.dotenv_utils import env_var_is_set, load_dotenv_paths
from clideps.ui.rich_output import format_success_or_failure

log = getLogger(__name__)


_log_api_setup_done = threading.Event()


def check_env_vars(env_vars: list[str] | None = None) -> list[tuple[CommonEnvVar, bool]]:
    """
    Checks which of the provided or default API keys are set in the
    environment or .env files.
    """
    if not env_vars:
        env_vars = get_all_common_env_vars()

    return [(CommonEnvVar(key), env_var_is_set(key)) for key in env_vars]


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


def format_env_check(env_vars: list[str] | None = None) -> Group:
    """
    Formats the status of API key setup as a Rich Group.
    """
    if not env_vars:
        env_vars = get_all_common_env_vars()

    dotenv_paths = load_dotenv_paths(True, True)

    dotenv_status_text = Text.assemble(
        format_success_or_failure(
            value=bool(dotenv_paths),
            true_str=f"Found .env files: {', '.join(str(path) for path in dotenv_paths)}",
            false_str="No .env files found. Set up your API keys in a .env file.",
        ),
    )

    api_key_status_texts = [
        format_success_or_failure(is_found, key.api_provider_name)
        for key, is_found in check_env_vars(env_vars)
    ]

    api_keys_found_text = Text.assemble("API keys found: ", Text(" ").join(api_key_status_texts))

    return Group(dotenv_status_text, api_keys_found_text)


def print_env_check(
    recommended_keys: list[str], env_vars: list[str] | None = None, once: bool = False
) -> None:
    """
    Convenience function to print status of whether all the given API keys
    were found in the environment or .env files.

    As a convenience, you can pass `once=True` and this will only ever log once.
    """
    if once and _log_api_setup_done.is_set():
        return

    output_group = format_env_check(env_vars)
    rprint(output_group)

    warn_if_missing_api_keys(recommended_keys)

    _log_api_setup_done.set()
