import logging
import math
from pathlib import Path

import yaml
from cachetools import TTLCache, cached
from prettyfmt import fmt_path

# pyright: reportImportCycles=false
from clideps.errors import UnknownPkgName
from clideps.pkgs.pkg_model import Pkg, PkgInfo, PkgName

log = logging.getLogger(__name__)


_PKG_DEPS_FILE = Path(__file__).parent / "common_pkgs.yml"


@cached(TTLCache(maxsize=math.inf, ttl=5.0))  # pyright: ignore
def load_pkg_info(*extra_sources: Path) -> dict[PkgName, PkgInfo]:  # noqa: F821
    """
    Loads package info definitions from the built-in YAML file and any additional
    sources. Later sources take precedence over earlier ones.
    """

    paths = [_PKG_DEPS_FILE, *extra_sources]
    pkg_info: dict[PkgName, PkgInfo] = {}
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Package info file file not found: {fmt_path(path)}")

        try:
            with open(_PKG_DEPS_FILE) as f:
                raw_data = yaml.safe_load(f)
            if not isinstance(raw_data, dict):
                raise TypeError("Expected YAML root to be a dictionary (map).")

            return {PkgName(name): PkgInfo.model_validate(data) for name, data in raw_data.items()}  # pyright: ignore
        except (yaml.YAMLError, TypeError, Exception) as e:
            log.exception(
                f"Error loading or parsing package dependencies from {fmt_path(path)}: {e}"
            )
            raise

    return pkg_info


def get_all_common_pkgs() -> list[Pkg]:
    """
    Get a list of all common packages.
    """
    from clideps.pkgs.pkg_info import load_pkg_info

    pkg_info = load_pkg_info()
    return [Pkg(name, info) for name, info in pkg_info.items()]


def get_pkg(pkg_name: PkgName) -> Pkg:
    """
    Look up a package by name, returning None if not found.
    """
    pkg_info = load_pkg_info().get(pkg_name)
    if not pkg_info:
        raise UnknownPkgName(f"Package info not found: {pkg_name}")
    return Pkg(pkg_name, pkg_info)


def validate_pkg_name(pkg_name: str) -> PkgName:
    """
    Validate a package name is a known package.
    """
    return get_pkg(pkg_name).name
