from collections.abc import Callable

import questionary


def input_confirm(
    prompt: str,
    instruction: str | None = None,
    default: bool = True,
) -> bool:
    return questionary.confirm(
        prompt,
        default=default,
        instruction=instruction,
    ).ask()


def input_simple_string(
    prompt: str,
    instruction: str | None = None,
    default: str = "",
    validate: Callable[[str], bool] | None = None,
) -> str:
    return questionary.text(
        prompt, instruction=instruction, default=default, validate=validate
    ).ask()
