from __future__ import annotations

from enum import Enum

from clideps.pkgs.pkg_types import PkgManager, Platform


class PkgManagers(Enum):
    brew = PkgManager(
        name="brew",
        url="https://github.com/Homebrew/brew",
        install_url="https://brew.sh/",
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
        platforms=(Platform.Darwin,),
        command_names=("port",),
        install_command_template=lambda args: f"port install {' '.join(args)}",
        version_command="port --version",
        priority=3,
    )
    apt = PkgManager(
        name="apt",
        url="https://debian-handbook.info/browse/stable/sect.apt-get.html",
        install_url=None,
        platforms=(Platform.Linux,),
        command_names=("apt-get", "apt"),
        install_command_template=lambda args: f"sudo apt-get update && sudo apt-get install -y {' '.join(args)}",
        version_command="apt --version",
        priority=2,
    )
    pixi = PkgManager(
        name="pixi",
        url="https://github.com/prefix-dev/pixi",
        install_url="https://pixi.sh/latest/",
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
        platforms=(Platform.Darwin, Platform.Linux, Platform.Windows),
        command_names=("pip", "pip3"),
        install_command_template=lambda args: f"pip install {' '.join(args)}",
        version_command="pip --version",
        priority=0,
    )
    winget = PkgManager(
        name="winget",
        url="https://github.com/microsoft/winget-cli",
        install_url="https://apps.microsoft.com/detail/9nblggh4nns1",
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
        platforms=(Platform.Windows,),
        command_names=("choco",),
        install_command_template=lambda args: f"choco install {' '.join(args)} -y",
        version_command="choco --version",
        priority=4,
    )


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
