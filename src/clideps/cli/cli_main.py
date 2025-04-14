"""
clideps is a cross-platform tool and library that helps you check if you
have messy dependencies set up right.

Check for external tools (like ffmpeg or ripgrep) and environment variables
(such as API keys) available.

And then it can help you install what you need!

More info: https://github.com/jlevy/clideps
"""

import argparse
import sys
from importlib.metadata import version

from clideps.cli.cli_commands import cli_pkg_check, cli_pkg_info
from clideps.errors import ClidepsError
from clideps.ui.argparse_utils import WrappedColorFormatter
from clideps.ui.rich_output import print_error

APP_NAME = "clideps"

APP_DESCRIPTION = """Dotenv and external tool dependencies with less pain"""


def get_app_version() -> str:
    try:
        return "v" + version(APP_NAME)
    except Exception:
        return "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=WrappedColorFormatter,
        description=f"{APP_DESCRIPTION}",
        epilog=(__doc__ or "") + "\n\n" + f"{APP_NAME} {get_app_version()}",
    )
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {get_app_version()}")
    parser.add_argument("--verbose", action="store_true", help="verbose output")

    # Parsers for each command.
    subparsers = parser.add_subparsers(dest="command", required=True)

    pkg_check_parser = subparsers.add_parser(
        "pkg_check",
        help="Check if the given packages are installed.",
        description="""
        Check if the given packages are installed. Names provided must be known packages,
        either common packages known to clideps or specified in a `pkg_info` field in a
        clideps.yml file.
        """,
        formatter_class=WrappedColorFormatter,
    )
    pkg_check_parser.add_argument("pkg_names", type=str, nargs="+", help="package names to check")

    pkg_info_parser = subparsers.add_parser(
        "pkg_info",
        help="Show information about a package.",
        description="Description 2.",
        formatter_class=WrappedColorFormatter,
    )
    pkg_info_parser.add_argument(
        "pkg_names", type=str, nargs="*", help="package names to show info for, or all if not given"
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "pkg_check":
            cli_pkg_check(args.pkg_names)
        elif args.command == "pkg_info":
            cli_pkg_info(args.pkg_names)
    except ClidepsError:
        # We will have already printed an error message.
        exit(1)
    except Exception as e:
        print_error(str(e))
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
