from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

PkgName: TypeAlias = str
"""Our name for a system package."""

CheckInfo: TypeAlias = str
"""
More info about a found package (like the command that was found) or a missing
package (like the exception message from the checker).
"""

InstallCommand: TypeAlias = str
"""A command to install a package."""

PkgTag: TypeAlias = str
"""Tags for a package."""

Url: TypeAlias = str
"""Use for URLs for better type clarity."""


class Platform(StrEnum):
    """
    The major platforms. We handle specific OS flavors (e.g. ubuntu vs debian) by just
    checking for package managers.
    """

    Darwin = "Darwin"
    Linux = "Linux"
    Windows = "Windows"


CommandTemplate: TypeAlias = Callable[[list[str]], InstallCommand]
"""Template for the command to install a package."""


@dataclass(frozen=True)
class PkgManager:
    name: str

    url: Url
    """URL for more info about the package manager. Preferably a GitHub repo."""

    install_url: Url | None
    """URL for installing the package manager. None if it's just a command."""

    install_command: InstallCommand | None
    """Command to install the package manager. Generally the primary cross-platform native way."""

    platforms: tuple[Platform, ...]
    """Platforms on which the package manager is available."""

    command_names: tuple[str, ...]
    """Names of the command to run the package manager."""

    install_command_template: CommandTemplate
    """Template for the command to install a package."""

    version_command: str
    """Command to check the version of the package manager and to confirm it is installed."""

    priority: int
    """Priority for the package manager. Lower is preferred."""

    # Sort by priority order.
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, PkgManager):
            return NotImplemented
        return (self.priority, self.name) < (other.priority, other.name)
