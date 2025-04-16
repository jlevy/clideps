from __future__ import annotations

from enum import Enum
from functools import cache

from clideps.pkgs.pkg_types import PkgManager, Platform


class PkgManagers(Enum):
    # TODO: Testing of more of these. Mostly only tested on macOS and ubuntu currently.

    brew = PkgManager(
        name="brew",
        url="https://github.com/Homebrew/brew",
        install_url="https://brew.sh/",
        install_command='/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        platforms=(Platform.Darwin,),
        command_names=("brew",),
        install_command_template=lambda args: f"brew install {' '.join(args)}",
        version_command="brew --version",
        priority=2,
    )

    macports = PkgManager(
        name="macports",
        url="https://macports.org/",
        install_url="https://macports.org/install.php",
        install_command=None,  # .pkg download on website
        platforms=(Platform.Darwin,),
        command_names=("port",),
        install_command_template=lambda args: f"port install {' '.join(args)}",
        version_command="port --version",
        priority=3,
    )

    apt = PkgManager(
        name="apt",
        url="https://wiki.debian.org/Apt",
        install_url=None,
        install_command=None,
        platforms=(Platform.Linux,),
        command_names=("apt", "apt-get"),
        install_command_template=lambda args: f"sudo apt-get install -y {' '.join(args)}",
        version_command="apt --version",
        priority=2,
    )

    dnf = PkgManager(
        name="dnf",
        url="https://github.com/rpm-software-management/dnf",
        install_url=None,  # Core OS component
        install_command=None,
        platforms=(Platform.Linux,),  # Fedora/RHEL
        command_names=("dnf",),
        install_command_template=lambda args: f"sudo dnf install -y {' '.join(args)}",
        version_command="dnf --version",
        priority=2,
    )

    pacman = PkgManager(
        name="pacman",
        url="https://archlinux.org/pacman/",
        install_url=None,  # Core OS component
        install_command=None,
        platforms=(Platform.Linux,),  # Arch
        command_names=("pacman",),
        install_command_template=lambda args: f"sudo pacman -S --noconfirm {' '.join(args)}",
        version_command="pacman --version",
        priority=2,
    )

    zypper = PkgManager(
        name="zypper",
        url="https://github.com/openSUSE/zypper",
        install_url=None,  # Core OS component
        install_command=None,
        platforms=(Platform.Linux,),  # openSUSE/SLES
        command_names=("zypper",),
        install_command_template=lambda args: f"sudo zypper install --non-interactive {' '.join(args)}",
        version_command="zypper --version",
        priority=2,
    )

    pixi = PkgManager(
        name="pixi",
        url="https://github.com/prefix-dev/pixi",
        install_url="https://pixi.sh/latest/",
        install_command="curl -fsSL https://pixi.sh/install.sh | sh",
        platforms=(Platform.Darwin, Platform.Linux, Platform.Windows),
        command_names=("pixi",),
        install_command_template=lambda args: f"pixi global install {' '.join(args)}",
        version_command="pixi --version",
        priority=1,
    )

    pip = PkgManager(
        name="pip",
        url="https://github.com/pypa/pip",
        install_url="https://pip.pypa.io/en/stable/installation/",
        install_command=None,
        platforms=(Platform.Darwin, Platform.Linux, Platform.Windows),
        command_names=("pip", "pip3"),
        install_command_template=lambda args: f"pip install {' '.join(args)}",
        version_command="pip --version",
        priority=0,
    )

    winget = PkgManager(
        name="winget",
        url="https://github.com/microsoft/winget-cli",
        install_url="https://apps.microsoft.com/detail/9NBLGGH4NNS1",
        install_command=None,
        platforms=(Platform.Windows,),
        command_names=("winget",),
        install_command_template=lambda args: f"winget install {' '.join(args)}",
        version_command="winget --version",
        priority=2,
    )

    scoop = PkgManager(
        name="scoop",
        url="https://github.com/ScoopInstaller/Scoop",
        install_url="https://scoop.sh/",
        install_command="Set-ExecutionPolicy RemoteSigned -Scope CurrentUser && Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression",
        platforms=(Platform.Windows,),
        command_names=("scoop",),
        install_command_template=lambda args: f"scoop install {' '.join(args)}",
        version_command="scoop --version",
        priority=3,
    )

    chocolatey = PkgManager(
        name="chocolatey",
        url="https://chocolatey.org/",
        install_url="https://chocolatey.org/install",
        install_command=None,  # So messy let's leave it alone for now.
        platforms=(Platform.Windows,),
        command_names=("choco",),
        install_command_template=lambda args: f"choco install {' '.join(args)} -y",
        version_command="choco --version",
        priority=4,
    )

    uv = PkgManager(
        name="uv",
        url="https://github.com/astral-sh/uv",
        install_url="https://docs.astral.sh/uv/getting-started/installation/",
        install_command="curl -LsSf https://astral.sh/uv/install.sh | sh",
        platforms=(Platform.Darwin, Platform.Linux, Platform.Windows),
        command_names=("uv",),
        install_command_template=lambda args: f"uv tool install {' '.join(args)}",
        version_command="uv --version",
        priority=1,
    )


@cache
def get_all_pkg_managers() -> list[PkgManager]:
    """
    Get all supported package managers.
    """
    return [pm.value for pm in PkgManagers]


def get_pkg_manager(name: str) -> PkgManager:
    """
    Get a package manager by name.
    """
    pm = next((pm for pm in PkgManagers if pm.name == name), None)
    if not pm:
        raise ValueError(f"Package manager not found: `{name}`")
    return pm.value
