import os
from pathlib import Path


def which_all(cmd: str) -> list[Path]:
    """
    Return list of full paths to executables matching `cmd` on `PATH`,
    honoring `PATHEXT` on Windows.

    Simplifies but extends `shutil.which()` for common use cases.

    Removes duplicates while preserving order based on PATH.
    Only intended for simple command names; raises ValueError if `cmd`
    contains a path separator.
    """
    if os.path.sep in cmd or (os.path.altsep and os.path.altsep in cmd):
        raise ValueError(f"cmd must be a simple name without path separators: '{cmd}'")

    paths = os.environ.get("PATH", "").split(os.pathsep)
    if os.name == "nt":
        # On Windows, set default extensions if PATHEXT is not set.
        exts = os.environ.get("PATHEXT", "").split(os.pathsep)
        if not any(exts):
            exts = [".COM", ".EXE", ".BAT", ".CMD"]
    else:
        exts = [""]
    matches: list[str] = []
    seen_paths: set[str] = set()

    for dir_path in paths:
        # Handle empty directory entries in PATH (means current directory)
        if not dir_path:
            dir_path = os.curdir
        for ext in exts:
            full_path = os.path.join(dir_path, cmd + ext)
            norm_full_path = os.path.normpath(full_path)
            if (
                norm_full_path not in seen_paths
                and os.path.isfile(full_path)
                and os.access(full_path, os.X_OK)
            ):
                matches.append(norm_full_path)
                seen_paths.add(norm_full_path)

    return [Path(p) for p in matches]
