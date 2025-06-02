

import click
import datetime
import pendulum
from sqlalchemy.orm import Session
from typing import Optional # Added Optional for potential use in options/arguments or clarity

from .database import create_all_tables, get_db
from .models import TreeType, Location, Stock, Transaction
from .inventory_manager import (
    create_tree_type, get_all_tree_types, get_tree_type_by_id,
    create_location, get_all_locations, get_location_by_id,
    add_stock_entry, get_all_stock_entries, get_stock_by_id,
    update_stock_quantity, move_stock_quantity,
    record_sale, get_all_transactions
)
from .utils import validate_positive_int, validate_positive_float, format_date, print_table

@click.group(help="GreenGrow Stock Manager: Manage your seedling inventory and sales.")
@click.pass_context
def cli(ctx):
    """
    GreenGrow Stock Manager CLI.
    Manages tree seedling inventory, locations, types, and sales.
    """
    ctx.obj = next(get_db())

@cli.command(name="init", help="Initializes the database and creates all tables.")
@click.pass_obj
def init_db(db: Session):
    """Initializes the database and creates all tables."""
    try:
        create_all_tables()
        click.echo(click.style("Database initialized successfully!", fg='green'))
    except Exception as e:
        click.echo(click.style(f"Error initializing database: {e}", fg='red'))
        click.abort()

# --- Tree Type Commands ---
@cli.command(name="add-type", help="Add a new tree seedling type.")
@click.argument("name")
@click.argument("base_price", type=float)
@click.option("--description", "-d", help="Optional description for the tree type.", default=None)
@click.pass_obj
def add_type(db: Session, name: str, base_price: float, description: Optional[str]): # Added Optional for description
    """Add a new tree seedling type."""
    base_price = validate_positive_float(str(base_price), "Base price")
    try:
        new_type = create_tree_type(db, name, base_price, description)
        click.echo(click.style(f"Tree type '{new_type.name}' (ID: {new_type.id}) added with price {new_type.base_unit_price:.2f}.", fg='green'))
    except Exception as e:
        click.echo(click.style(f"Error adding tree type: {e}", fg='red'))
        click.abort()

@cli.command(name="list-types", help="List all registered tree seedling types.")
@click.pass_obj
def list_types(db: Session):
    """List all registered tree seedling types."""
    types = get_all_tree_types(db)
    if not types:
        click.echo("No tree types registered yet.")
        return

    headers = ["ID", "Name", "Base Price", "Description"]
    rows = []
    for t in types:
        rows.append([t.id, t.name, f"${t.base_unit_price:.2f}", t.description if t.description else "N/A"])
    print_table(headers, rows)

# --- Location Commands ---
@cli.command(name="add-location", help="Add a new storage location.")
@click.argument("name")
@click.option("--description", "-d", help="Optional description for the location.", default=None)
@click.pass_obj
def add_location(db: Session, name: str, description: Optional[str]): # Added Optional for description
    """Add a new storage location."""
    try:
        new_location = create_location(db, name, description)
        click.echo(click.style(f"Location '{new_location.name}' (ID: {new_location.id}) added.", fg='green'))
    except Exception as e:
        click.echo(click.style(f"Error adding location: {e}", fg='red'))
        click.abort()

@cli.command(name="list-locations", help="List all registered storage locations.")
@click.pass_obj
def list_locations(db: Session):
    """List all registered storage locations."""
    locations = get_all_locations(db)
    if not locations:
        click.echo("No locations registered yet.")
        return

    headers = ["ID", "Name", "Description"]
    rows = []
    for loc in locations:
        rows.append([loc.id, loc.name, loc.description if loc.description else "N/A"])
    print_table(headers, rows)

# --- Stock Commands ---
@cli.command(name="add-stock", help="Add new stock of a seedling type to a location.")
@click.argument("type_id", type=int)
@click.argument("location_id", type=int)
@click.argument("quantity", type=int)
@click.option("--cost", "-c", "cost_per_seedling", type=float, help="Cost paid per seedling for this batch.", default=0.0)
@click.pass_obj
def add_stock(db: Session, type_id: int, location_id: int, quantity: int, cost_per_seedling: float):
    """Add new stock of a seedling type to a location."""
    quantity = validate_positive_int(str(quantity), "Quantity")
    cost_per_seedling = validate_positive_float(str(cost_per_seedling), "Cost per seedling")

    tree_type = get_tree_type_by_id(db, type_id)
    location = get_location_by_id(db, location_id)

    if not tree_type:
        click.echo(click.style(f"Error: Tree type with ID {type_id} not found.", fg='red'))
        click.abort()
    if not location:
        click.echo(click.style(f"Error: Location with ID {location_id} not found.", fg='red'))
        click.abort()

    try:
        new_stock = add_stock_entry(db, type_id, location_id, quantity, cost_per_seedling)
        click.echo(click.style(f"Added {new_stock.quantity} '{new_stock.tree_type.name}' seedlings (Stock ID: {new_stock.id}) to '{new_stock.location.name}'.", fg='green'))
    except Exception as e:
        click.echo(click.style(f"Error adding stock: {e}", fg='red'))
        click.abort()

@cli.command(name="move-stock", help="Move quantity of seedlings from one stock entry to another location.")
@click.argument("from_stock_id", type=int)
@click.argument("to_location_id", type=int)
@click.argument("quantity", type=int)
@click.pass_obj
def move_stock(db: Session, from_stock_id: int, to_location_id: int, quantity: int):
    """Move quantity of seedlings from one stock entry to another location."""
    quantity = validate_positive_int(str(quantity), "Quantity")

    from_stock = get_stock_by_id(db, from_stock_id)
    to_location = get_location_by_id(db, to_location_id)

    if not from_stock:
        click.echo(click.style(f"Error: Source Stock ID {from_stock_id} not found.", fg='red'))
        click.abort()
    if not to_location:
        click.echo(click.style(f"Error: Destination Location ID {to_location_id} not found.", fg='red'))
        click.abort()
    if from_stock.quantity < quantity:
        click.echo(click.style(f"Error: Not enough stock ({from_stock.quantity}) in Stock ID {from_stock_id} to move {quantity}.", fg='red'))
        click.abort()

    try:
        # The return type of move_stock_quantity is Optional[Tuple[Stock, Stock]]
        # We need to ensure it's not None before unpacking.
        result = move_stock_quantity(db, from_stock_id, to_location_id, quantity)
        if result: # Check if result is not None
            updated_from_stock, updated_to_stock = result
            click.echo(click.style(
                f"Moved {quantity} '{updated_from_stock.tree_type.name}' seedlings from '{updated_from_stock.location.name}' "
                f"(now {updated_from_stock.quantity} remaining) to '{updated_to_stock.location.name}' "
                f"(now {updated_to_stock.quantity} total).", fg='green'
            ))
        else: # This else block should ideally not be reached if checks above are thorough, but good for safety.
            click.echo(click.style("Failed to move stock due to an internal error.", fg='red'))
            click.abort()
    except Exception as e:
        click.echo(click.style(f"Error moving stock: {e}", fg='red'))
        click.abort()

@cli.command(name="view-inventory", help="View current inventory of seedlings.")
@click.option("--type", "-t", "type_id", type=Optional[int], help="Filter by Tree Type ID.", default=None) # Added Optional
@click.option("--location", "-l", "location_id", type=Optional[int], help="Filter by Location ID.", default=None) # Added Optional
@click.pass_obj
def view_inventory(db: Session, type_id: Optional[int], location_id: Optional[int]): # Added Optional for parameters
    """View current inventory of seedlings."""
    stocks = get_all_stock_entries(db, tree_type_id=type_id, location_id=location_id)
    if not stocks:
        click.echo("No stock entries found matching the criteria.")
        return

    headers = ["Stock ID", "Tree Type", "Location", "Quantity", "Unit Price", "Total Value", "Date Added"]
    rows = []
    total_inventory_value = 0.0

    for stock in stocks:
        total_value = stock.quantity * stock.tree_type.base_unit_price
        total_inventory_value += total_value
        rows.append([
            stock.id,
            stock.tree_type.name,
            stock.location.name,
            stock.quantity,
            f"${stock.tree_type.base_unit_price:.2f}",
            f"${total_value:.2f}",
            format_date(stock.date_added)
        ])
    print_table(headers, rows)
    click.echo(click.style(f"\nTotal Estimated Inventory Value: ${total_inventory_value:.2f}", fg='magenta', bold=True))

# --- Sales Commands ---
@cli.command(name="record-sale", help="Record a sale of seedlings.")
@click.argument("type_id", type=int)
@click.argument("quantity", type=int)
@click.pass_obj
def record_sale_cmd(db: Session, type_id: int, quantity: int):
    """Record a sale of seedlings."""
    quantity = validate_positive_int(str(quantity), "Quantity")

    tree_type = get_tree_type_by_id(db, type_id)
    if not tree_type:
        click.echo(click.style(f"Error: Tree type with ID {type_id} not found.", fg='red'))
        click.abort()

    try:
        transaction = record_sale(db, type_id, quantity)
        if transaction:
            click.echo(click.style(
                f"Recorded sale of {transaction.quantity_sold} '{transaction.tree_type.name}' seedlings for ${transaction.total_amount:.2f}.",
                fg='green'
            ))
        else:
            click.echo(click.style(f"Error: Not enough stock of '{tree_type.name}' to sell {quantity}.", fg='red'))
            click.abort()
    except Exception as e:
        click.echo(click.style(f"Error recording sale: {e}", fg='red'))
        click.abort()

@cli.command(name="view-sales-history", help="View past sales transactions.")
@click.option("--start-date", "-s", type=Optional[str], help="Filter sales from this date (YYYY-MM-DD).", default=None) # Added Optional
@click.option("--end-date", "-e", type=Optional[str], help="Filter sales up to this date (YYYY-MM-DD).", default=None) # Added Optional
@click.pass_obj
def view_sales_history(db: Session, start_date: Optional[str], end_date: Optional[str]): # Added Optional for parameters
    """View past sales transactions."""
    parsed_start_date = None
    parsed_end_date = None

    if start_date:
        try:
            parsed_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            click.echo(click.style("Invalid start date format. Please use YYYY-MM-DD.", fg='red'))
            click.abort()
    if end_date:
        try:
            parsed_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            click.echo(click.style("Invalid end date format. Please use YYYY-MM-DD.", fg='red'))
            click.abort()

    transactions = get_all_transactions(db, start_date=parsed_start_date, end_date=parsed_end_date)
    if not transactions:
        click.echo("No sales transactions found matching the criteria.")
        return

    headers = ["Transaction ID", "Tree Type", "Quantity Sold", "Unit Price", "Total Amount", "Date"]
    rows = []
    total_revenue = 0.0

    for t in transactions:
        total_revenue += t.total_amount
        rows.append([
            t.id,
            t.tree_type.name,
            t.quantity_sold,
            f"${t.unit_sale_price_at_time_of_sale:.2f}",
            f"${t.total_amount:.2f}",
            format_date(t.transaction_date)
        ])
    print_table(headers, rows)
    click.echo(click.style(f"\nTotal Revenue for Period: ${total_revenue:.2f}", fg='magenta', bold=True))

if __name__ == "__main__":
    cli()