import os
from enum import Enum
from pathlib import Path
from typing import overload

from typing_extensions import override


class _RequiredType:
    @override
    def __repr__(self) -> str:
        return "REQUIRED"


REQUIRED = _RequiredType()
"""Sentinel value to indicate a required environment variable."""


class MissingEnvVar(ValueError):
    """Exception raised when an environment variable is not set."""

    def __init__(self, env_var: str):
        super().__init__(f"Required environment variable is not set: {env_var}")


class EnvEnum(str, Enum):
    """
    Convenience base class for environment variables for an application. Subclass
    and define enum members to represent environment variables that can be
    read in various formats.

    Example:
    ```
    class MyEnv(EnvEnum):
        MY_API_KEY = "MY_API_KEY"
        MY_DEBUG_MODE = "MY_DEBUG_MODE"
        MY_CONFIG_PATH = "MY_CONFIG_PATH"

    # Required value (raises ValueError if not set)
    api_key = MyEnv.API_KEY.read_str()

    # Optional with default
    debug = MyEnv.MY_DEBUG_MODE.read_bool(default=False)

    # Optional that can be None
    config_path = MyEnv.MY_CONFIG_PATH.read_path(default=None)
    ```
    """

    @overload
    def read_str(self) -> str: ...  # Required

    @overload
    def read_str(self, *, default: str) -> str: ...

    @overload
    def read_str(self, *, default: None) -> str | None: ...  # Default is None

    def read_str(self, *, default: str | None | _RequiredType = REQUIRED) -> str | None:
        """
        Get the string value of the environment variable.
        Raises `MissingEnvVar` (a `ValueError` subclass) if variable is not set and
        no default is provided.
        """
        env_value = os.environ.get(self.value)

        if env_value is not None:
            return env_value  # Variable is set

        if isinstance(default, _RequiredType):
            raise MissingEnvVar(self.value)
        else:
            return default

    @overload
    def read_path(self) -> Path: ...  # Required

    @overload
    def read_path(self, *, default: Path) -> Path: ...

    @overload
    def read_path(self, *, default: None) -> Path | None: ...

    def read_path(
        self, *, default: Path | None | _RequiredType = REQUIRED
    ) -> Path | None:
        """
        Get the Path value of the environment variable.
        Raises `MissingEnvVar` (a `ValueError` subclass) if variable is not set and
        no default is provided.
        """
        env_value_str = os.environ.get(self.value)

        if env_value_str is not None:
            return Path(env_value_str).expanduser().resolve()

        if isinstance(default, _RequiredType):
            raise MissingEnvVar(self.value)
        elif default is None:
            return None
        else:
            return default.expanduser().resolve()

    @overload
    def read_bool(self) -> bool: ...

    @overload
    def read_bool(self, *, default: bool) -> bool: ...

    def read_bool(self, *, default: bool | _RequiredType = REQUIRED) -> bool:
        """
        Get the boolean value of the environment variable.
        Raises `MissingEnvVar` (a `ValueError` subclass) if variable is not set and
        no default is provided.
        """
        env_value_str = os.environ.get(self.value)

        if env_value_str is not None:
            # Variable is set, parse its string value
            processed_value = str(env_value_str or "").strip().lower()
            return bool(
                processed_value
                and processed_value != "0"
                and processed_value != "false"
                and processed_value != "no"
                and processed_value != "off"
            )
        else:
            if isinstance(default, _RequiredType):
                raise MissingEnvVar(self.value)
            else:
                return default
