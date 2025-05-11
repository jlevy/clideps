"""
clideps is a cross-platform tool and library that helps with the headache
of checking your system setup and if you have various dependencies set up right.

More info: https://github.com/jlevy/clideps
"""

import argparse
import logging
import sys
from importlib.metadata import version

from clideps.cli.cli_commands import (
    cli_env_check,
    cli_pkg_check,
    cli_pkg_info,
    cli_pkg_manager_check,
    cli_terminal_info,
    cli_warn_if_missing,
)
from clideps.ui.rich_output import print_error, rprint
from clideps.ui.styles import STYLE_HINT
from clideps.utils.readable_argparse import ReadableColorFormatter

APP_NAME = "clideps"

APP_DESCRIPTION = """Terminal environment setup with less pain"""


def get_app_version() -> str:
    try:
        return "v" + version(APP_NAME)
    except Exception:
        return "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=ReadableColorFormatter,
        description=f"{APP_DESCRIPTION}",
        epilog=(__doc__ or "") + "\n\n" + f"{APP_NAME} {get_app_version()}",
    )
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {get_app_version()}")
    parser.add_argument("--verbose", action="store_true", help="verbose output")
    parser.add_argument("--debug", action="store_true", help="debug output")

    # Parsers for each command.
    subparsers = parser.add_subparsers(dest="command", required=True)

    pkg_info_parser = subparsers.add_parser(
        "pkg_info",
        help="Show general info about given packages.",
        description="""
        Show general info about given packages. Does not check if they are installed.
        """,
        formatter_class=ReadableColorFormatter,
    )
    pkg_info_parser.add_argument(
        "pkg_names", type=str, nargs="*", help="package names to show info for, or all if not given"
    )

    pkg_check_parser = subparsers.add_parser(
        "pkg_check",
        help="Check if the given packages are installed.",
        description="""
        Check if the given packages are installed. Names provided must be known packages,
        either common packages known to clideps or specified in a `pkg_info` field in a
        clideps.yml file.
        """,
    )
    pkg_check_parser.add_argument("pkg_names", type=str, nargs="*", help="package names to check")

    warn_if_missing_parser = subparsers.add_parser(
        "warn_if_missing",
        help="Warn if the given packages are not installed.",
        description="""
        Warn if the given packages are not installed. Also give suggestions for
        how to install them.
        """,
        formatter_class=ReadableColorFormatter,
    )
    warn_if_missing_parser.add_argument(
        "pkg_names", type=str, nargs="+", help="package names to warn for"
    )

    subparsers.add_parser(
        "pkg_manager_check",
        help="Check which package managers are installed.",
        description="Check which package managers (brew, apt, scoop, etc.) are installed and available.",
        formatter_class=ReadableColorFormatter,
    )

    env_check_parser = subparsers.add_parser(
        "env_check",
        help="Show information about .env files and environment variables.",
        description="""
        Show information about .env files and environment variables.
        """,
        formatter_class=ReadableColorFormatter,
    )
    env_check_parser.add_argument(
        "env_vars",
        type=str,
        nargs="*",
        help="""
        environment variables to show info for (if none, use some common API keys
        like OPENAI_API_KEY, AZURE_API_KEY, etc.)
        """,
    )

    subparsers.add_parser(
        "terminal_info",
        help="Show information about the terminal.",
        description="""
        Show information about the terminal. Includes regular terminfo details and
        whether the terminal supports other features like hyperlinks or images.
        """,
        formatter_class=ReadableColorFormatter,
    )

    subparsers.add_parser(
        "check",
        help="""
        Run all checks to show terminal, package manager, .env, and status of common packages.
        """,
        description="""
        Run all checks to show terminal, package manager, .env, and status of common packages.
        Same as running `terminal_info`, `pkg_manager_check`, `env_check`, and `pkg_check`.
        """,
        formatter_class=ReadableColorFormatter,
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    try:
        if args.command == "pkg_info":
            cli_pkg_info(args.pkg_names)
        elif args.command == "pkg_check":
            cli_pkg_check(args.pkg_names)
        elif args.command == "warn_if_missing":
            cli_warn_if_missing(args.pkg_names)
        elif args.command == "pkg_manager_check":
            cli_pkg_manager_check()
        elif args.command == "env_check":
            cli_env_check(args.env_vars)
        elif args.command == "terminal_info":
            cli_terminal_info()
        elif args.command == "check":
            cli_terminal_info()
            cli_pkg_manager_check()
            cli_env_check([])
            cli_pkg_check([])

    except Exception as e:
        print_error(str(e))
        rprint("Use --verbose or --debug to see the full traceback.", style=STYLE_HINT)
        rprint()
        if args.verbose or args.debug:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
