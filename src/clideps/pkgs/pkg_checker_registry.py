from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TypeAlias

from strif import AtomicVar

from clideps.errors import ConfigError
from clideps.pkgs.pkg_model import CheckInfo, PkgName

log = logging.getLogger(__name__)


Checker: TypeAlias = Callable[[], None | bool]
"""
A checker should raise an exception (with a descriptive message)
or return False on failure. Returning True or None indicates that
the package is available.
"""

_checker_registry: AtomicVar[dict[str, Checker]] = AtomicVar({})


def register_pkg_checker(pkg_name: PkgName) -> Callable[[Checker], Checker]:
    """
    Decorator to register a checker function for a package.
    """

    def decorator(func: Checker) -> Checker:
        with _checker_registry.updates() as registry:
            if pkg_name in registry:
                raise ConfigError(f"Checker '{pkg_name}' is already registered.")
            registry[pkg_name] = func
        return func

    return decorator


def get_checker(name: PkgName) -> Checker | None:
    """Retrieve a checker function from the registry by name."""
    return _checker_registry.copy().get(name)


def run_checker(name: PkgName) -> tuple[bool, CheckInfo]:
    """
    Run the checker function for a package.
    """
    checker = get_checker(name)
    if checker:
        try:
            checker_result = checker()
            if checker_result is False:
                return False, f"Package `{name}` not found (checker failed)"
            else:
                return True, f"Package `{name}` found (checker passed)"
        except Exception as e:
            log.info("Package %r is not installed or not accessible (checker failed): %s", name, e)
            return False, f"Package `{name}` not found (checker failed): {e}"
    return False, f"Package `{name}` not found (no command or checker found)"
