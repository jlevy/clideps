from clideps.env.env_check import print_env_check
from clideps.errors import UnknownPkgName
from clideps.pkgs.pkg_check import pkg_check
from clideps.pkgs.pkg_info import get_pkg_info, load_pkg_info
from clideps.terminal.terminal_features import terminal_check
from clideps.ui.rich_output import print_error, rprint


def cli_pkg_info(pkg_names: list[str]) -> None:
    all_pkg_info = load_pkg_info()
    names_to_show = sorted(pkg_names or list(all_pkg_info.keys()))

    if not names_to_show:
        rprint("No packages found to display info for.")
        return

    for name in names_to_show:
        try:
            pkg = get_pkg_info(name)
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
    rprint()
    rprint(result.formatted())
    rprint()


def cli_env_check(env_vars: list[str]) -> None:
    rprint()
    print_env_check(env_vars)
    rprint()


def cli_terminal_info() -> None:
    rprint()
    rprint(terminal_check().formatted())
    rprint()
