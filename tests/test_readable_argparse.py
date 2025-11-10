import argparse

from rich.markdown import Markdown

from clideps.utils.readable_argparse import (
    ReadableColorFormatter,
    default_text_wrapper,
    get_readable_console_width,
)


def test_readable_console_width() -> None:
    width = get_readable_console_width()
    assert 40 <= width <= 100

    width = get_readable_console_width(min_width=50, max_width=80)
    assert 50 <= width <= 80


def test_text_wrapper() -> None:
    # Plain text mode
    result = default_text_wrapper("Test text", as_markdown=False)
    assert result == "Test text"
    assert isinstance(result, str)

    # Markdown mode - returns Markdown object for rich_argparse to render
    result = default_text_wrapper("# Test\n\nSome text", as_markdown=True)
    assert isinstance(result, Markdown)


def test_formatter_instantiation() -> None:
    # Default formatter
    parser = argparse.ArgumentParser(
        prog="test",
        formatter_class=ReadableColorFormatter,
    )
    assert parser.formatter_class == ReadableColorFormatter

    # With markdown formatting
    parser = argparse.ArgumentParser(
        prog="test",
        description="# Test\n\nMarkdown description",
        formatter_class=lambda prog: ReadableColorFormatter(prog, format_markdown=True),
    )
    help_text = parser.format_help()
    assert help_text
    # Markdown header is rendered (not raw), so check for "Test" text
    assert "Test" in help_text
    assert "Markdown description" in help_text

    # Without console wrapping
    parser = argparse.ArgumentParser(
        prog="test",
        formatter_class=lambda prog: ReadableColorFormatter(prog, wrap_to_console=False),
    )
    help_text = parser.format_help()
    assert help_text

    # Without action spacing
    parser = argparse.ArgumentParser(
        prog="test",
        formatter_class=lambda prog: ReadableColorFormatter(prog, add_action_spacing=False),
    )
    help_text = parser.format_help()
    assert help_text


def test_markdown_rendering() -> None:
    """Test that markdown actually gets rendered with proper styling."""
    # Direct markdown description (rich_argparse should handle this)
    parser = argparse.ArgumentParser(
        prog="test",
        description=Markdown("# Title\n\n**Bold text** and `code`"),  # pyright: ignore[reportArgumentType]
        formatter_class=ReadableColorFormatter,
    )
    help_text = parser.format_help()
    assert "Title" in help_text

    # With format_markdown=True
    parser2 = argparse.ArgumentParser(
        prog="test",
        description="# Title\n\n**Bold text** and `code`",
        formatter_class=lambda prog: ReadableColorFormatter(prog, format_markdown=True),
    )
    help_text2 = parser2.format_help()
    assert "Title" in help_text2
    # Check that markdown syntax appears (may or may not be styled in tests)
    assert "Bold text" in help_text2 or "**Bold text**" in help_text2


def test_width_control() -> None:
    """Test that width control works."""
    # Narrow width
    parser = argparse.ArgumentParser(
        prog="test",
        description="This is a very long description that should be wrapped to a narrower width when we set max_width to a small value",
        formatter_class=lambda prog: ReadableColorFormatter(
            prog, max_width=50, wrap_to_console=True
        ),
    )
    help_text = parser.format_help()
    assert help_text
    # Lines should be relatively short (accounting for indentation)
    lines = [line for line in help_text.split("\n") if line.strip()]
    # Most lines in description should be under 60 chars (50 + some margin)
    long_lines = [line for line in lines if len(line) > 70]
    # Allow some long lines for usage/options but most should be wrapped
    assert len(long_lines) < len(lines) // 2
