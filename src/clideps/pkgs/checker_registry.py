from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TypeAlias

from clideps.errors import ConfigError
from clideps.pkgs.pkg_model import PkgName
from clideps.utils.atomic_var import AtomicVar

log = logging.getLogger(__name__)


Checker: TypeAlias = Callable[[], None | bool]
"""
A checker should raise an exception or return False on failure. Returning
True or None indicates that the package is available.
"""

_checker_registry: AtomicVar[dict[str, Checker]] = AtomicVar({})


def register_checker(name: PkgName) -> Callable[[Checker], Checker]:
    """
    Decorator to register a checker function for a package.
    """

    def decorator(func: Checker) -> Checker:
        with _checker_registry.updates() as registry:
            if name in registry:
                raise ConfigError(f"Checker '{name}' is already registered.")
            registry[name] = func
        return func

    return decorator


def get_checker(name: PkgName) -> Checker | None:
    """Retrieve a checker function from the registry by name."""
    return _checker_registry.copy().get(name)


def run_checker(name: PkgName) -> bool:
    """
    Run the checker function for a package.
    """
    checker = get_checker(name)
    if checker:
        try:
            return bool(checker())
        except Exception as e:
            log.info("Package %r is not installed or not accessible (checker failed): %s", name, e)
            return False
    return False
