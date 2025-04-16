from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

import yaml
from pydantic import BaseModel
from rich.console import Group
from rich.text import Text

# pyright: reportImportCycles=false
from clideps.errors import PkgMissing
from clideps.pkgs.common_pkg_managers import get_all_pkg_managers
from clideps.pkgs.pkg_types import CheckInfo, InstallCommand, PkgManager, PkgName, Platform
from clideps.pkgs.platform_checks import get_platform
from clideps.ui.rich_output import format_name_and_value, format_status, format_success_or_failure
from clideps.ui.styles import STYLE_HEADING, STYLE_HINT


class PkgInstallNames(BaseModel):
    """
    Install names for each package manager for a given package.
    """

    brew: str | None = None
    apt: str | None = None
    dnf: str | None = None
    pacman: str | None = None
    zypper: str | None = None
    pixi: str | None = None
    pip: str | None = None
    winget: str | None = None
    scoop: str | None = None
    chocolatey: str | None = None
    macports: str | None = None


class PkgInfo(BaseModel):
    """
    Information about a system package dependency (e.g. a library or command-line
    tool) and how to install it on each applicable platform.
    """

    command_names: tuple[str, ...]
    """Commands offered by the package (if any)."""

    install_names: PkgInstallNames = PkgInstallNames()
    """Install names for each package manager."""

    tags: tuple[str, ...] = ()
    """Tags for the package."""

    comment: str | None = None
    """Notes about the package or its availability on each platform. Shown to the user if present."""

    def to_yaml(self) -> str:
        """Serialize the PkgInfo to YAML format."""

        data = self.model_dump(exclude_defaults=True)  # Exclude defaults for cleaner YAML
        return yaml.dump(data, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> PkgInfo:
        data = yaml.safe_load(yaml_str)
        return cls.model_validate(data)


@dataclass(frozen=True, order=True)
class Pkg:
    """
    A package is a our name plus associated info.
    """

    name: PkgName
    info: PkgInfo

    def can_be_installed_with(self, pm: PkgManager) -> bool:
        """
        Check if this package can be installed with the given package manager.
        """
        return getattr(self.info.install_names, pm.name, None) is not None

    def get_applicable_pms(self) -> list[PkgManager]:
        """
        Get the list of package managers that can install this package.
        """
        return [pm for pm in get_all_pkg_managers() if self.can_be_installed_with(pm)]

    def get_applicable_platforms(self) -> list[Platform]:
        """
        Get the list of platforms where we know how to install this package.
        """
        platforms: set[Platform] = set()
        for pm in self.get_applicable_pms():
            platforms.update(pm.platforms)
        return list(platforms)

    def get_install_name(self, pm: PkgManager) -> str:
        """
        Get the package name for use with the given package manager.
        """
        install_name = getattr(self.info.install_names, pm.name)
        if not install_name:
            raise ValueError(
                f"Install name for `{self.name}` under package manager `{pm.name}` not "
                f"found, only have: {self.info.install_names}"
            )
        return install_name

    def format_install_info(self) -> Group:
        """
        Formatted info on how to install a given package using available package managers.
        """
        install_commands = get_install_commands(self.get_applicable_pms(), self.name)
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

    def formatted_info(self) -> Group:
        """
        Formatted info about a package.
        """
        texts: list[Text | Group] = []

        if self.info.command_names:
            cmds_str = ", ".join(f"`{cmd}`" for cmd in self.info.command_names)
            texts.append(Text.assemble(("Commands: ", STYLE_HINT), (cmds_str, "")))

        if self.info.comment:
            texts.append(Text(self.info.comment, style=STYLE_HINT))

        texts.append(self.format_install_info())

        return Group(*texts)

    def formatted(self) -> Group:
        tests: list[Text | Group] = []
        tests.append(Text(f"{self.name}", STYLE_HEADING))
        tests.append(self.formatted_info())

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
            doc = format_status(True, found_str)
            texts.append(doc)
        for pkg in self.missing_required:
            missing_str = self.missing_info.get(pkg.name, "Required package not found!")
            doc = format_status("error", missing_str)
            texts.append(doc)
        for pkg in self.missing_recommended:
            missing_str = self.missing_info.get(pkg.name, "Recommended package not found")
            doc = format_status("warning", missing_str)
            texts.append(doc)
        for pkg in self.missing_optional:
            missing_str = self.missing_info.get(pkg.name, "Optional package not found")
            doc = format_status("info", missing_str)
            texts.append(doc)

        return Group(*texts)

    def is_found(self, pkg_name: PkgName) -> bool:
        return any(pkg.name == pkg_name for pkg in self.found_pkgs)

    def require(self, *pkg_names: PkgName, on_platforms: list[Platform] | None = None) -> None:
        """
        Require a package to be installed. If `on_platforms` is provided, the package will only be
        required if the current platform is in the list.
        """
        if on_platforms and get_platform() not in on_platforms:
            return

        for pkg_name in pkg_names:
            if not self.is_found(pkg_name):
                # print_missing_tool_help(pkg)
                raise PkgMissing(f"`{pkg_name}` needed but not found")

    def missing(self, *pkg_names: PkgName) -> list[PkgName]:
        return [pkg_name for pkg_name in pkg_names if not self.is_found(pkg_name)]

    def warn_if_missing(self, *pkg_names: PkgName) -> list[PkgName]:
        from clideps.pkgs.install_suggestions import print_missing_pkg_warning

        missing = self.missing(*pkg_names)
        if missing:
            print_missing_pkg_warning(*missing)
        return missing

    def status(self) -> Text:
        texts: list[Text] = []
        for pkg in self.found_pkgs:
            texts.append(format_success_or_failure(True, pkg.name))

        return Text.assemble("Local system packages found: ", Text(" ").join(texts))


def get_install_command(pkg_manager: PkgManager, *pkgs: Pkg) -> InstallCommand:
    """
    Get the install command for a package manager to install a list of packages.
    """
    install_names = [pkg.get_install_name(pkg_manager) for pkg in pkgs]
    return pkg_manager.install_command_template(list(install_names))


def get_install_commands(
    pkg_managers: list[PkgManager], *pkg_names: PkgName
) -> dict[PkgManager, InstallCommand]:
    """
    Get the install commands for a list of package managers to install a list of packages,
    consolidating commands for each package manager.
    """
    from clideps.pkgs.pkg_info import get_pkg

    installable_with: dict[PkgManager, list[Pkg]] = defaultdict(list)
    for pkg_name in pkg_names:
        for pm in sorted(pkg_managers):
            pkg = get_pkg(pkg_name)
            if pkg.can_be_installed_with(pm):
                installable_with[pm].append(pkg)

    install_info: dict[PkgManager, InstallCommand] = {}
    for pm, pkgs_for_pm in installable_with.items():
        install_command = get_install_command(pm, *pkgs_for_pm)
        if install_command:
            install_info[pm] = install_command

    return install_info
