

import click
import datetime
import pendulum
from typing import List # Added List for Python 3.8 compatibility

def validate_positive_int(value: str, field_name: str) -> int:
    """Validates if a string can be converted to a positive integer."""
    try:
        num = int(value)
        if num <= 0:
            click.echo(click.style(f"Error: {field_name} must be a positive integer.", fg='red'))
            raise click.Abort()
        return num
    except ValueError:
        click.echo(click.style(f"Error: {field_name} must be a valid integer.", fg='red'))
        raise click.Abort()

def validate_positive_float(value: str, field_name: str) -> float:
    """Validates if a string can be converted to a positive float."""
    try:
        num = float(value)
        if num < 0:
            click.echo(click.style(f"Error: {field_name} cannot be negative.", fg='red'))
            raise click.Abort()
        return num
    except ValueError:
        click.echo(click.style(f"Error: {field_name} must be a valid number.", fg='red'))
        raise click.Abort()

def format_date(dt: datetime.datetime) -> str:
    """Formats a datetime object to a readable string."""
    return pendulum.instance(dt).format("YYYY-MM-DD HH:mm:ss")

def print_table(headers: List[str], rows: List[List[str]]): # Changed list[list] to List[List]
    """Prints data in a simple table format."""
    if not rows:
        click.echo("No data to display.")
        return

    # Calculate column widths
    column_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            column_widths[i] = max(column_widths[i], len(str(cell)))

    # Print header
    header_line = " | ".join(f"{header:<{column_widths[i]}}" for i, header in enumerate(headers))
    click.echo(click.style(header_line, fg='cyan', bold=True))
    click.echo(click.style("-" * len(header_line), fg='cyan'))

    # Print rows
    for row in rows:
        row_line = " | ".join(f"{str(cell):<{column_widths[i]}}" for i, cell in enumerate(row))
        click.echo(row_line)