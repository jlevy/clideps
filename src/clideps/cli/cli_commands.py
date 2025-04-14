from clideps.errors import UnknownPkgName
from clideps.pkgs.pkg_check import pkg_check
from clideps.pkgs.pkg_info import get_pkg_info, load_pkg_info
from clideps.ui.rich_output import print_error, rprint


def cli_pkg_info(pkg_names: list[str]) -> None:
    """
    Display information about the requested packages.
    """
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
    """
    Check if the requested packages are installed.
    """
    result = pkg_check(pkg_names)
    rprint()
    rprint(result.formatted())
    rprint()
