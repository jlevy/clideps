from pathlib import Path

from prettyfmt import fmt_lines, fmt_path
from rich import print as rprint
from strif import abbrev_str

from clideps.env_vars.dotenv_utils import (
    env_var_is_set,
    find_dotenv_paths,
    read_dotenv_file,
    update_env_file,
)
from clideps.ui.inputs import input_confirm, input_simple_string
from clideps.ui.rich_output import format_failure, format_success, print_heading, print_status


def interactive_dotenv_setup(
    api_keys: list[str],
    update: bool = False,
) -> None:
    """
    Interactively configure your .env file with the requested API key
    environment variables.

    :param all: Configure all known API keys (instead of just recommended ones).
    :param update: Update values even if they are already set.
    """

    if not update:
        api_keys = [key for key in api_keys if not env_var_is_set(key)]

    rprint()
    print_heading("Configuring .env file")
    if api_keys:
        rprint(format_failure(f"API keys needed: {', '.join(api_keys)}"))
        interactive_update_dotenv(api_keys)
    else:
        rprint(format_success("All requested API keys are set!"))


CWD_DOTENV_PATH = Path(".") / ".env.local"


def interactive_update_dotenv(
    keys: list[str], fallback_env_path: Path = CWD_DOTENV_PATH, *extra_dirs: Path
) -> bool:
    """
    Interactively fill missing values in the active .env file.
    Uses `fallback_env_path` if no .env file is found in the extra dirs.
    If no `fallback_env_path` is provided, uses `./.env.local`.
    Returns True if the user made changes, False otherwise.
    """
    dotenv_paths = find_dotenv_paths(True, *extra_dirs)
    dotenv_path = dotenv_paths[0] if dotenv_paths else None

    if dotenv_path:
        print_status(f"Found existing .env, so we can update it: {fmt_path(dotenv_path)}")
        old_dotenv = read_dotenv_file(dotenv_path)
        if old_dotenv:
            rprint("Current values:")
            summary = fmt_lines(
                [f"{k} = {repr(abbrev_str(v or '', 12))}" for k, v in old_dotenv.items()]
            )
            rprint(f"File has {len(old_dotenv)} keys:\n{summary}")
    else:
        dotenv_path = fallback_env_path
        print_status(f"No .env file found, so we will create one here: {fmt_path(dotenv_path)}")

    if input_confirm(
        "Do you want make updates to this .env file?",
        instruction="This will leave all env vars in that file intact unless you confirm an update to them.",
        default=True,
    ):
        dotenv_path_str = input_simple_string("Path to the .env file: ", default=str(dotenv_path))
        if not dotenv_path_str:
            print_status("Config changes cancelled.")
            return False

        dotenv_path = Path(dotenv_path_str)

        rprint()
        rprint("We will update the following keys from %s:\n%s", dotenv_path, fmt_lines(keys))
        rprint()
        rprint(
            "Enter values for each key, or press enter to skip changes for that key. Values need not be quoted."
        )

        updates: dict[str, str] = {}
        for key in keys:
            value = input_simple_string(
                f"Enter value for {key}:",
                instruction='Leave empty to skip, use "" for a true empty string.',
            )
            if value and value.strip():
                updates[key] = value
            else:
                rprint(f"Skipping {key}. Will not change this key.")

        # Actually save the collected variables to the .env file
        update_env_file(dotenv_path, updates, create_if_missing=True)
        rprint()
        rprint(format_success(f"{len(updates)} API keys saved to {dotenv_path}"))
        rprint()
        rprint(
            "You can always edit the .env file directly if you need to, or "
            "rerun `self_configure` to update your configs again."
        )
    else:
        print_status("Config changes cancelled.")
        return False

    return True
