import logging
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from prettyfmt import fmt_path
from rich.console import Group
from rich.text import Text

from clideps.pkgs.common_pkg_managers import PkgManagers
from clideps.pkgs.pkg_model import PkgManager
from clideps.pkgs.platform_checks import get_platform
from clideps.ui.rich_output import STYLE_HINT, format_status

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PkgManagerCheckResult:
    """
    Result of checking whether a single package manager is installed.
    """

    pkg_manager: PkgManager
    path: Path | None = None
    version_output: str | None = None

    def formatted(self) -> Text:
        details: list[str] = []
        if self.version_output:
            first_line = self.version_output.splitlines()[0].strip()
            if first_line:
                details.append(first_line)
        if self.path:
            details.append(f"at {fmt_path(self.path)}")

        details_str = " ".join(details)
        message = Text.assemble((f"{self.pkg_manager.name}", ""), (f" ({details_str})", STYLE_HINT))
        return format_status(True, message)


@dataclass(frozen=True)
class PkgManagerCheckResults:
    """
    Results of checking what package managers are installed.
    """

    found: list[PkgManagerCheckResult]
    missing: list[PkgManager]

    def formatted(self) -> Group:
        items: list[Text] = []
        if self.found:
            items.extend(fm.formatted() for fm in self.found)
        if self.missing:
            items.extend(
                format_status(
                    "info",
                    Text.assemble((f"{pm.name}", ""), (" (not found)", STYLE_HINT)),
                )
                for pm in self.missing
            )
        return Group(*items)


def pkg_manager_check() -> PkgManagerCheckResults:
    """
    Check which package managers are installed on the current platform,
    returning detailed results for found and missing managers.
    """
    found_pkg_managers: list[PkgManagerCheckResult] = []
    missing_pkg_managers: list[PkgManager] = []
    current_platform = get_platform()

    for pm_enum in PkgManagers:
        pm = pm_enum.value

        # Skip if not applicable to this platform.
        if current_platform not in pm.platforms:
            continue

        # Assume missing initially for this platform.
        is_missing = True
        found_path: Path | None = None
        version_output: str | None = None

        # Determine if in path first (for more descriptive error message).
        base_command = pm.version_command.split()[0]
        found_path_str = shutil.which(base_command)

        if found_path_str:
            found_path = Path(found_path_str)
            # Now run the full check command
            try:
                log.debug(f"Checking for {pm.name} using: '{pm.version_command}'")
                result = subprocess.run(
                    pm.version_command,
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                version_output = result.stdout.strip()
                log.info(
                    f"{pm.name} found (exit code {result.returncode}). Path: {found_path}. Output:\n{version_output}"
                )
                # If command succeeded, it's not missing
                is_missing = False
            except FileNotFoundError:
                log.info(f"Check command for {pm.name} not found: '{pm.version_command}'")
            except subprocess.CalledProcessError as e:
                log.info(
                    f"Check command for {pm.name} failed (exit code {e.returncode}): {pm.version_command}\nError: {e.stderr or e.stdout}"
                )
            except Exception as e:
                log.warning(
                    f"Error checking for {pm.name} with command '{pm.version_command}': {e}"
                )
        else:
            log.info(f"Command '{base_command}' for {pm.name} not found in PATH.")

        # Append to the correct list
        if is_missing:
            missing_pkg_managers.append(pm)
        else:
            # We only add to found if version_output is not None, implying the check command ran successfully.
            if version_output is not None:
                found_pkg_managers.append(
                    PkgManagerCheckResult(
                        pkg_manager=pm, path=found_path, version_output=version_output
                    )
                )
            else:
                # Should not happen if is_missing is False, but as a safeguard
                log.warning(
                    f"Manager {pm.name} was marked as found, but version output is missing."
                )
                missing_pkg_managers.append(pm)

    log.info(
        f"Found {len(found_pkg_managers)} package managers: {', '.join(fm.pkg_manager.name for fm in found_pkg_managers)}"
    )
    return PkgManagerCheckResults(found=found_pkg_managers, missing=missing_pkg_managers)
