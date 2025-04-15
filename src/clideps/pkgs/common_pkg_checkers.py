from clideps.pkgs.pkg_checker_registry import register_pkg_checker


@register_pkg_checker("libmagic")
def check_libmagic() -> bool:
    """Check if the libmagic library is installed and functional."""
    import magic  # pyright: ignore

    magic.Magic()  # pyright: ignore
    return True
