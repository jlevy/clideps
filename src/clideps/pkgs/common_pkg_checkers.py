from clideps.pkgs.checker_registry import register_checker


@register_checker("libmagic")
def check_libmagic() -> bool:
    """Check if the libmagic library is installed and functional."""
    import magic  # pyright: ignore

    magic.Magic()  # pyright: ignore
    return True
