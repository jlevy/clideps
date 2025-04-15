import logging
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from prettyfmt import fmt_path
from rich.text import Text

from clideps.pkgs.pkg_model import PkgManager, PkgManagers
from clideps.pkgs.platform_checks import get_platform
from clideps.ui.rich_output import STYLE_HINT, format_status

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PkgManagerCheckResult:
    """Result of checking a single package manager."""

    pm: PkgManager
    path: Path | None = None
    version_output: str | None = None

    def formatted(self) -> Text:
        """Return a formatted string for display."""
        details: list[str] = []
        if self.version_output:
            first_line = self.version_output.splitlines()[0].strip()
            if first_line:
                details.append(first_line)
        if self.path:
            details.append(f"at {fmt_path(self.path)}")

        details_str = " ".join(details)
        message = Text.assemble((f"`{self.pm.name}`", ""), (f" ({details_str})", STYLE_HINT))
        return format_status(True, message, space=" ")


def pkg_manager_check() -> list[PkgManagerCheckResult]:
    """
    Check which package managers are installed on the current platform,
    returning detailed results for each found manager.
    """
    found_pkg_managers: list[PkgManagerCheckResult] = []
    current_platform = get_platform()

    for pm_enum in PkgManagers:
        pm = pm_enum.value
        if current_platform not in pm.platforms:
            log.debug(f"Skipping {pm.name}, not supported on {current_platform}")
            continue

        # Determine if in path first (for more descriptive error message).
        base_command = pm.check_command.split()[0]
        found_path_str = shutil.which(base_command)
        if not found_path_str:
            log.info(f"Command '{base_command}' for {pm.name} not found in PATH.")
            continue

        found_path = Path(found_path_str)

        # Now run the full check command
        try:
            log.debug(f"Checking for {pm.name} using: '{pm.check_command}'")
            # Use shell=True cautiously, but needed for commands like 'cmd --version'
            # Capture output to prevent polluting stdout/stderr
            result = subprocess.run(
                pm.check_command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )
            version_output = result.stdout.strip()
            log.info(
                f"{pm.name} found (exit code {result.returncode}). Path: {found_path}. Output:\n{version_output}"
            )
            found_pkg_managers.append(
                PkgManagerCheckResult(pm=pm, path=found_path, version_output=version_output)
            )
        except FileNotFoundError:
            # This case should technically be caught by shutil.which, but handled for robustness.
            log.info(f"Check command for {pm.name} not found: '{pm.check_command}'")
        except subprocess.CalledProcessError as e:
            log.info(
                f"Check command for {pm.name} failed (exit code {e.returncode}): {pm.check_command}\nError: {e.stderr or e.stdout}"
            )
        except Exception as e:
            log.warning(f"Error checking for {pm.name} with command '{pm.check_command}': {e}")

    return found_pkg_managers
