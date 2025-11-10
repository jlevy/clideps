"""
clideps is a cross-platform tool and library that helps with the headache
of checking your system setup and if you have various dependencies set up right.

More info: https://github.com/jlevy/clideps
"""

import argparse
import logging
import sys
from importlib.metadata import version
from textwrap import dedent

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

APP_DESCRIPTION = dedent("""
    **Terminal environment setup with less pain**

    A cross-platform tool and library for checking your system setup and dependencies.

    Use `clideps check` to run all checks, or use individual commands for specific checks.
    """).strip()


def markdown_formatter(prog: str) -> ReadableColorFormatter:
    """Helper to create ReadableColorFormatter with markdown enabled."""
    return ReadableColorFormatter(prog, format_markdown=True)


def get_app_version() -> str:
    try:
        return "v" + version(APP_NAME)
    except Exception:
        return "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=markdown_formatter,
        description=APP_DESCRIPTION,
        epilog=f"More info: https://github.com/jlevy/clideps\n\n{APP_NAME} {get_app_version()}",
    )
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {get_app_version()}")
    parser.add_argument("--verbose", action="store_true", help="verbose output")
    parser.add_argument("--debug", action="store_true", help="debug output")

    # Parsers for each command.
    subparsers = parser.add_subparsers(dest="command", required=True)

    pkg_info_parser = subparsers.add_parser(
        "pkg_info",
        help="Show general info about given packages.",
        description=dedent("""
            Show general info about given packages.

            Does **not** check if they are installed.
            """).strip(),
        formatter_class=markdown_formatter,
    )
    pkg_info_parser.add_argument(
        "pkg_names",
        type=str,
        nargs="*",
        help="package names to show info for (all if not specified)",
    )

    pkg_check_parser = subparsers.add_parser(
        "pkg_check",
        help="Check if the given packages are installed.",
        description=dedent("""
            Check if the given packages are installed.

            Names provided must be **known packages**, either:
            - Common packages known to clideps, or
            - Specified in a `pkg_info` field in a `clideps.yml` file
            """).strip(),
        formatter_class=markdown_formatter,
    )
    pkg_check_parser.add_argument("pkg_names", type=str, nargs="*", help="package names to check")

    warn_if_missing_parser = subparsers.add_parser(
        "warn_if_missing",
        help="Warn if the given packages are not installed.",
        description=dedent("""
            Warn if the given packages are **not installed** and provide installation suggestions.
            """).strip(),
        formatter_class=markdown_formatter,
    )
    warn_if_missing_parser.add_argument(
        "pkg_names", type=str, nargs="+", help="package names to warn for"
    )

    subparsers.add_parser(
        "pkg_manager_check",
        help="Check which package managers are installed.",
        description=dedent("""
            Check which package managers (`brew`, `apt`, `scoop`, etc.) are installed and available.
            """).strip(),
        formatter_class=markdown_formatter,
    )

    env_check_parser = subparsers.add_parser(
        "env_check",
        help="Show information about .env files and environment variables.",
        description=dedent("""
            Show information about `.env` files and environment variables.

            Checks both:
            - Environment variables currently set
            - Variables defined in `.env` files
            """).strip(),
        formatter_class=markdown_formatter,
    )
    env_check_parser.add_argument(
        "env_vars",
        type=str,
        nargs="*",
        help="environment variables to check (common API keys if not specified)",
    )

    subparsers.add_parser(
        "terminal_info",
        help="Show information about the terminal.",
        description=dedent("""
            Show information about the terminal, including:
            - Regular terminfo details
            - Support for features like **hyperlinks** or **images**
            """).strip(),
        formatter_class=markdown_formatter,
    )

    subparsers.add_parser(
        "check",
        help="Run all checks to show terminal, package manager, .env, and status of common packages.",
        description=dedent("""
            Run all checks to show:
            - Terminal info
            - Package manager status
            - Environment variables
            - Common package status

            Same as running `terminal_info`, `pkg_manager_check`, `env_check`, and `pkg_check` sequentially.
            """).strip(),
        formatter_class=markdown_formatter,
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
