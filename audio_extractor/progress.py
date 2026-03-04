from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
)
from rich.console import Console

console = Console()


def make_progress() -> Progress:
    return Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    )


def print_summary(succeeded: int, skipped: int, failed: int) -> None:
    console.print()
    console.print("[bold]Batch Summary[/bold]")
    console.print(f"  [green]✓ Succeeded:[/green] {succeeded}")
    console.print(f"  [yellow]⊘ Skipped:[/yellow]   {skipped}")
    console.print(f"  [red]✗ Failed:[/red]    {failed}")
    console.print()
