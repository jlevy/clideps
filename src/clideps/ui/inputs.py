from collections.abc import Callable

import questionary

Validator = Callable[[str], bool | str | None]


def input_confirm(
    prompt: str,
    *,
    instruction: str | None = None,
    default: bool = True,
) -> bool:
    """
    Get a yes/no confirmation from the user.

    Args:
        prompt: The question to ask
        instruction: Optional help text
        default: Default value if user just presses enter
    """
    return questionary.confirm(
        prompt,
        default=default,
        instruction=instruction,
    ).ask()


def input_simple_string(
    prompt: str,
    *,
    instruction: str | None = None,
    default: str = "",
    validate: Validator | None = None,
    multiline: bool = False,
    required: bool = True,
) -> str:
    """
    Get simple text input from the user with validation.

    Args:
        prompt: The question/prompt to show
        instruction: Optional help text for the user
        default: Default value if user just presses enter
        validate: Function to validate input. Should return:
            - True: input is valid
            - False: input is invalid (uses default error message)
            - str: input is invalid with custom error message
            - None: input is valid (treated same as True)
        multiline: Allow multi-line input
        required: Whether input is required (if False, empty input is allowed)
    """

    def _wrapped_validator(value: str) -> bool | str:
        # Handle the required check first
        if not required and not value.strip():
            return True

        if validate is None:
            return True

        result = validate(value)
        # Convert None to True for compatibility
        return True if result is None else result

    return questionary.text(
        prompt,
        instruction=instruction,
        default=default,
        validate=_wrapped_validator,
        multiline=multiline,
    ).ask()
