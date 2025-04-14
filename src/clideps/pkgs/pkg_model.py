from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import TypeAlias

import yaml
from pydantic import BaseModel
from rich.console import Group
from rich.text import Text

from clideps.ui.rich_output import format_name_and_value, format_success_or_failure
from clideps.ui.styles import STYLE_HEADING, STYLE_HINT

PkgName: TypeAlias = str
"""Our name for a system package."""

CheckInfo: TypeAlias = str
"""
More info about a found package (like the command that was found) or a missing
package (like the exception message from the checker).
"""

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


CommandTemplate: TypeAlias = Callable[[list[str]], str]


@dataclass(frozen=True)
class PkgManager:
    name: str
    url: Url
    install_url: Url | None
    platforms: tuple[Platform, ...]
    command_names: tuple[str, ...]
    install_command_template: CommandTemplate

    def get_install_command(self, *pkg_names: str) -> str:
        return self.install_command_template(list(pkg_names))


class PkgManagers(Enum):
    brew = PkgManager(
        name="brew",
        url="https://github.com/Homebrew/brew",
        install_url="https://brew.sh/",
        platforms=(Platform.Darwin,),
        command_names=("brew",),
        install_command_template=lambda args: f"brew install {' '.join(args)}",
    )
    apt = PkgManager(
        name="apt",
        url="https://debian-handbook.info/browse/stable/sect.apt-get.html",
        install_url=None,
        platforms=(Platform.Linux,),
        command_names=("apt-get",),
        install_command_template=lambda args: f"apt-get install {' '.join(args)}",
    )
    pixi = PkgManager(
        name="pixi",
        url="https://github.com/prefix-dev/pixi",
        install_url="https://pixi.sh/latest/",
        platforms=(Platform.Darwin, Platform.Linux, Platform.Windows),
        command_names=("pixi",),
        install_command_template=lambda args: f"pixi global install {' '.join(args)}",
    )
    pip = PkgManager(
        name="pip",
        url="https://github.com/pypa/pip",
        install_url="https://pip.pypa.io/en/stable/installation/",
        platforms=(Platform.Darwin, Platform.Linux, Platform.Windows),
        command_names=("pip",),
        install_command_template=lambda args: f"pip install {' '.join(args)}",
    )
    winget = PkgManager(
        name="winget",
        url="https://github.com/microsoft/winget-cli",
        install_url="https://apps.microsoft.com/detail/9nblggh4nns1",
        platforms=(Platform.Windows,),
        command_names=("winget",),
        install_command_template=lambda args: f"winget install {' '.join(args)}",
    )
    chocolatey = PkgManager(
        name="chocolatey",
        url="https://chocolatey.org/",
        install_url="https://chocolatey.org/install",
        platforms=(Platform.Windows,),
        command_names=("choco",),
        install_command_template=lambda args: f"choco install {' '.join(args)}",
    )


class PkgManagerNames(BaseModel):
    brew: str | None = None
    apt: str | None = None
    pixi: str | None = None
    pip: str | None = None
    winget: str | None = None
    chocolatey: str | None = None

    def install_info(self) -> dict[PkgManager, str]:
        """
        Return all install info for this package for each package manager.
        """
        install_info: dict[PkgManager, str] = {}
        for pm in PkgManagers:
            pkg_install_name = getattr(self, pm.name, None)
            if pkg_install_name:
                install_info[pm.value] = pm.value.get_install_command(pkg_install_name)
        return install_info

    def formatted(self) -> Group:
        """
        Formatted info on how to install a given package using available package managers.
        """
        install_commands = self.install_info()
        if not install_commands:
            return Group()

        install_texts: list[Text] = []
        for pkg_manager, install_command in install_commands.items():
            install_texts.append(
                format_name_and_value(
                    f"{pkg_manager.name} ({', '.join(pkg_manager.platforms)})",
                    f"`{install_command}`",
                    extra_indent="  ",
                )
            )

        # Combine the header and the list items
        return Group(Text("Available via:", style=STYLE_HINT), *install_texts)


class PkgInfo(BaseModel):
    """
    Information about a system package dependency (e.g. a library or command-line
    tool) and how to install it on each applicable platform.
    """

    command_names: tuple[str, ...]
    """Commands offered by the package (if any)."""

    pkg_managers: PkgManagerNames = PkgManagerNames()
    """Package manager install names."""

    comment: str | None = None
    """Notes about the package or its availability on each platform."""

    def to_yaml(self) -> str:
        """Serialize the PkgInfo to YAML format."""

        data = self.model_dump(exclude_defaults=True)  # Exclude defaults for cleaner YAML
        return yaml.dump(data, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> PkgInfo:
        data = yaml.safe_load(yaml_str)
        return cls.model_validate(data)

    def formatted(self) -> Group:
        """
        Formatted info about a package.
        """
        texts: list[Text | Group] = []

        if self.command_names:
            cmds_str = ", ".join(f"`{cmd}`" for cmd in self.command_names)
            texts.append(Text.assemble(("Commands: ", STYLE_HINT), (cmds_str, "")))

        if self.comment:
            texts.append(Text(self.comment, style=STYLE_HINT))
        # Get the formatted install options from PkgManagerNames
        install_group = self.pkg_managers.formatted()
        if install_group:
            texts.append(install_group)

        return Group(*texts)


@dataclass(frozen=True)
class Pkg:
    """
    A package is a our name plus associated info.
    """

    name: PkgName
    info: PkgInfo

    def formatted(self) -> Group:
        tests: list[Text | Group] = []
        tests.append(Text(f"{self.name}", STYLE_HEADING))
        tests.append(self.info.formatted())
        return Group(*tests)


class DepType(Enum):
    """The type of dependency."""

    optional = "optional"
    recommended = "recommended"
    mandatory = "mandatory"


@dataclass(frozen=True)
class PkgDep:
    """
    A dependency on a system package.
    """

    pkg_name: PkgName
    pkg_info: PkgInfo
    dep_type: DepType

    @property
    def pkg(self) -> Pkg:
        return Pkg(self.pkg_name, self.pkg_info)


@dataclass(frozen=True)
class DepDeclarations:
    """
    A list of declared optional, recommended, and/or mandatory dependencies.
    """

    deps: list[PkgDep]


@dataclass(frozen=True)
class PkgCheckResult:
    """
    Package check results about which tools are installed.
    """

    found_pkgs: list[Pkg]
    missing_required: list[Pkg]
    missing_recommended: list[Pkg]
    missing_optional: list[Pkg]
    found_info: dict[PkgName, CheckInfo]
    missing_info: dict[PkgName, CheckInfo]

    def formatted(self) -> Group:
        texts: list[Text | Group] = []
        for pkg in self.found_pkgs:
            found_str = self.found_info.get(pkg.name, "Found")
            doc = format_success_or_failure(
                True,
                true_str=format_name_and_value(pkg.name, found_str),
                false_str=format_name_and_value(pkg.name, "Not found!"),
            )
            texts.append(doc)

        for pkg in self.missing_required:
            missing_str = self.missing_info.get(pkg.name, "Not found!")
            doc = format_success_or_failure(
                False,
                true_str=format_name_and_value(pkg.name, missing_str),
                false_str=format_name_and_value(pkg.name, "Not found!"),
            )

        return Group(*texts)
