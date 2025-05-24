import logging
from typing import Dict, List, Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    console = Console()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 使用 RichHandler
    rich_handler = RichHandler(
        console=console,
        show_time=False,
        show_path=False,
        rich_tracebacks=True,
        markup=True,
    )
    rich_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(message)s")
    rich_handler.setFormatter(formatter)

    logger.addHandler(rich_handler)

    return logger


def print_separator(logger: logging.Logger, char: str = "─", length: int = 80) -> None:

    logger.info(char * length)


def print_header(logger: logging.Logger, title: str) -> None:

    console = Console()
    panel = Panel(title, border_style="bold blue", expand=False)
    console.print(panel)


def print_category_result(logger: logging.Logger, category: str, stats: dict) -> None:
    if stats["total"] > 0:
        avg_acc = stats["correct"] / stats["total"]
        logger.info(
            f"[bold]{category:<40}[/bold] | "
            f"[cyan]Total: {stats['total']:>6}[/cyan] | "
            f"[green]Correct: {stats['correct']:>6}[/green] | "
            f"[yellow]Accuracy: {avg_acc:.2%}[/yellow]"
        )


def print_results_table(logger: logging.Logger, category_stats: dict) -> None:
    console = Console()
    table = Table(
        title="Category-wise Results",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
    )

    table.add_column("Category", style="bold", width=40)
    table.add_column("Total", justify="right", style="cyan")
    table.add_column("Correct", justify="right", style="green")
    table.add_column("Accuracy", justify="right", style="yellow")

    total_samples = 0
    total_correct = 0

    for category, stats in category_stats.items():
        if stats["total"] > 0:
            avg_acc = stats["correct"] / stats["total"]
            table.add_row(
                category, str(stats["total"]), str(stats["correct"]), f"{avg_acc:.2%}"
            )
            total_samples += stats["total"]
            total_correct += stats["correct"]

    # 添加总计行
    if total_samples > 0:
        overall_acc = total_correct / total_samples
        table.add_row(
            "[bold]Overall[/bold]",
            str(total_samples),
            str(total_correct),
            f"{overall_acc:.2%}",
            style="bold"
        )

    console.print(table)


def print_detailed_results(logger: logging.Logger, task_results: List[Dict]) -> None:
    console = Console()
    table = Table(
        title="Detailed Task Results",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
    )

    table.add_column("Task ID", style="bold", width=50)
    table.add_column("Total", justify="right", style="cyan")
    table.add_column("Correct", justify="right", style="green")
    table.add_column("Accuracy", justify="right", style="yellow")

    total_samples = 0
    total_correct = 0

    for result in task_results:
        table.add_row(
            result["task_id"],
            str(result["total"]),
            str(result["correct"]),
            f"{result['acc']:.2%}",
        )
        total_samples += result["total"]
        total_correct += result["correct"]

    # 添加总计行
    if total_samples > 0:
        overall_acc = total_correct / total_samples
        table.add_row(
            "[bold]Overall[/bold]",
            str(total_samples),
            str(total_correct),
            f"{overall_acc:.2%}",
            style="bold"
        )

    console.print(table)
