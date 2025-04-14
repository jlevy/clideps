import subprocess
from pathlib import Path
from typing import Any

import questionary

from clideps.errors import CommandCancelled, CommandFailed
from clideps.ui.rich_output import print_success, rprint
from clideps.ui.styles import EMOJI_FAILURE


def run_command_with_confirmation(
    command: str,
    description: str | None = None,
    cwd: Path | None = None,
    capture_output: bool = True,
) -> str:
    """
    Print a command, ask for confirmation, and run it if confirmed.
    """
    if description:
        rprint()
        rprint(f"Step: [bold]{description}[/bold]")
    rprint()
    rprint(f"Will run: [bold]❯[/bold] [bold blue]{command}[/bold blue]")
    rprint()

    if not questionary.confirm("Run this command?", default=True).ask():
        raise CommandCancelled()

    try:
        rprint()
        rprint(
            f"[bold yellow]Running:[/bold yellow] [bold]❯[/bold] [bold blue]{command}[/bold blue]"
        )
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=capture_output,
            cwd=cwd,
        )
        if result.stdout:
            rprint(result.stdout)
        print_success("Command executed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        rprint(
            f"[bold red]{EMOJI_FAILURE} Command failed with exit code: {e.returncode}[/bold red]"
        )
        if e.stdout:
            rprint(e.stdout)
        if e.stderr:
            rprint(f"[red]{e.stderr}[/red]")
        raise CommandFailed() from e


def run_commands_sequence(
    commands: list[tuple[str, str]], cwd: Path, **format_args: Any
) -> list[str]:
    """
    Run a sequence of commands with confirmation. Each command is formatted with
    the provided arguments.
    """
    rprint(f"Working from directory: [bold blue]{cwd.absolute()}[/bold blue]")
    rprint()
    results: list[str] = []
    for cmd_template, description in commands:
        cmd = cmd_template.format(**format_args)
        result = run_command_with_confirmation(cmd, description, cwd=cwd)
        results.append(result)

    return results
