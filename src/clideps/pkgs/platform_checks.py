import platform
import shutil
from dataclasses import dataclass
from functools import cache

from clideps.pkgs.pkg_types import PkgManager, Platform


@cache
def get_platform() -> Platform:
    """
    The current platform.
    """
    return Platform(platform.system())


def compatible_pkg_managers() -> list[PkgManager]:
    """
    Package managers that are compatible with the current platform.
    """
    from clideps.pkgs.common_pkg_managers import PkgManagers

    platform = get_platform()
    return [
        pkg_manager.value for pkg_manager in PkgManagers if platform in pkg_manager.value.platforms
    ]


@dataclass(frozen=True)
class PkgManagerCheckResult:
    """Result of checking which package managers are installed."""

    found: list[PkgManager]
    compatible: list[PkgManager]


def get_available_pkg_managers() -> PkgManagerCheckResult:
    """
    Checks if any known package managers are available.
    """

    found: list[PkgManager] = []
    compatible: list[PkgManager] = []

    for manager in compatible_pkg_managers():
        is_installed = any(shutil.which(cmd) for cmd in manager.command_names)
        if is_installed:
            found.append(manager)
        else:
            compatible.append(manager)

    return PkgManagerCheckResult(found=found, compatible=compatible)
