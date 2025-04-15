# pyright: reportImportCycles=false
from clideps.pkgs.pkg_info import get_pkg
from clideps.pkgs.pkg_manager_check import pkg_manager_check
from clideps.pkgs.pkg_model import Pkg, get_install_commands
from clideps.pkgs.pkg_types import PkgName
from clideps.ui.rich_output import format_name_and_value, print_warning, rprint
from clideps.ui.styles import STYLE_HINT


def print_install_suggestion(*pkg_names: PkgName) -> str | None:
    pm_results = pkg_manager_check()
    found_pms = [fm.pkg_manager for fm in pm_results.found]
    install_commands = get_install_commands(found_pms, *pkg_names)
    if install_commands:
        rprint("You can install packages with a package manager you already use:")
        rprint()
        for pm, install_command in install_commands.items():
            rprint(format_name_and_value(pm.name, f"`{install_command}`"))
    else:
        rprint(
            "It doesn't look like any of your currently installed package managers "
            "can install this directly."
        )
        rprint("However, you can install it using one of these package managers:")
        rprint()
        for pm in pm_results.missing:
            rprint(format_name_and_value(pm.name, str(pm.install_url)))

    return None


def print_missing_pkg_warning(*pkg_names: PkgName):
    for pkg_name in pkg_names:
        print_warning(f"{pkg_name} was not found")
        rprint("It is recommended to install it for better functionality.", style=STYLE_HINT)
        pkg: Pkg = get_pkg(pkg_name)
        if pkg.info.comment:
            rprint(pkg.info.comment, style=STYLE_HINT)

    rprint()
    print_install_suggestion(*pkg_names)


# FIXME: Now need to add functions to run these for you, with confirmation.
