from clideps.env_vars.env_check import print_env_check
from clideps.errors import UnknownPkgName
from clideps.pkgs.pkg_check import pkg_check, warn_if_missing
from clideps.pkgs.pkg_info import get_pkg, load_pkg_info
from clideps.pkgs.pkg_manager_check import pkg_manager_check
from clideps.terminal.terminal_features import terminal_check
from clideps.ui.rich_output import print_error, print_heading, print_warning, rprint


def cli_pkg_info(pkg_names: list[str]) -> None:
    all_pkg_info = load_pkg_info()
    names_to_show = sorted(pkg_names or list(all_pkg_info.keys()))

    print_heading("Package Info")
    if not names_to_show:
        print_warning("No packages found to display info for.")
        return

    for name in names_to_show:
        try:
            pkg = get_pkg(name)
            rprint(pkg.formatted())
            rprint()
        except KeyError:
            print_error(f"Package '{name}' not found.")
            raise UnknownPkgName(name) from None
        except Exception as e:
            print_error(f"Could not get package info for '{name}': {e}")
            raise


def cli_pkg_check(pkg_names: list[str]) -> None:
    if pkg_names:
        result = pkg_check(pkg_names)
    else:
        result = pkg_check()
    print_heading("Package Check Results")
    rprint(result.formatted())
    rprint()


def cli_warn_if_missing(pkg_names: list[str]) -> None:
    warn_if_missing(pkg_names)


def cli_env_check(env_vars: list[str]) -> None:
    print_env_check(env_vars)
    rprint()


def cli_terminal_info() -> None:
    print_heading("Terminal Info")
    rprint(terminal_check().formatted())
    rprint()


def cli_pkg_manager_check() -> None:
    installed_managers = pkg_manager_check()
    if installed_managers:
        print_heading("Package Manager Status")
        rprint(installed_managers.formatted())
    else:
        print_warning("No supported package managers found")
    rprint()
