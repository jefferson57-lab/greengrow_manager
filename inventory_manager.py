

import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import TreeType, Location, Stock, Transaction
from .database import get_db
from .utils import validate_positive_int, validate_positive_float, format_date
from typing import List, Optional, Tuple # Added List, Optional, Tuple for Python 3.8 compatibility

# --- TreeType Operations ---

def create_tree_type(db: Session, name: str, base_price: float, description: Optional[str] = None) -> TreeType:
    """Creates a new tree type."""
    db_tree_type = TreeType(name=name, base_unit_price=base_price, description=description)
    db.add(db_tree_type)
    db.commit()
    db.refresh(db_tree_type)
    return db_tree_type

def get_tree_type_by_id(db: Session, tree_type_id: int) -> Optional[TreeType]: # Changed TreeType | None to Optional[TreeType]
    """Retrieves a tree type by its ID."""
    return db.query(TreeType).filter(TreeType.id == tree_type_id).first()

def get_all_tree_types(db: Session) -> List[TreeType]: # Changed list[TreeType] to List[TreeType]
    """Retrieves all tree types."""
    return db.query(TreeType).all()

# --- Location Operations ---

def create_location(db: Session, name: str, description: Optional[str] = None) -> Location:
    """Creates a new location."""
    db_location = Location(name=name, description=description)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def get_location_by_id(db: Session, location_id: int) -> Optional[Location]: # Changed Location | None to Optional[Location]
    """Retrieves a location by its ID."""
    return db.query(Location).filter(Location.id == location_id).first()

def get_all_locations(db: Session) -> List[Location]: # Changed list[Location] to List[Location]
    """Retrieves all locations."""
    return db.query(Location).all()

# --- Stock Operations ---

def add_stock_entry(db: Session, tree_type_id: int, location_id: int, quantity: int, cost_per_seedling: float = 0.0) -> Stock:
    """Adds a new stock entry for a tree type at a location."""
    db_stock = Stock(
        tree_type_id=tree_type_id,
        location_id=location_id,
        quantity=quantity,
        cost_per_seedling=cost_per_seedling
    )
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

def get_stock_by_id(db: Session, stock_id: int) -> Optional[Stock]: # Changed Stock | None to Optional[Stock]
    """Retrieves a stock entry by its ID."""
    return db.query(Stock).filter(Stock.id == stock_id).first()

def get_all_stock_entries(db: Session, tree_type_id: Optional[int] = None, location_id: Optional[int] = None) -> List[Stock]: # Changed list[Stock] to List[Stock], added Optional for parameters
    """Retrieves all stock entries, with optional filters."""
    query = db.query(Stock)
    if tree_type_id:
        query = query.filter(Stock.tree_type_id == tree_type_id)
    if location_id:
        query = query.filter(Stock.location_id == location_id)
    return query.all()

def update_stock_quantity(db: Session, stock_id: int, new_quantity: int) -> Optional[Stock]: # Changed Stock | None to Optional[Stock]
    """Updates the quantity of a specific stock entry."""
    db_stock = get_stock_by_id(db, stock_id)
    if db_stock:
        db_stock.quantity = new_quantity
        db.commit()
        db.refresh(db_stock)
    return db_stock

def move_stock_quantity(db: Session, from_stock_id: int, to_location_id: int, quantity_to_move: int) -> Optional[Tuple[Stock, Stock]]: # Changed tuple[Stock, Stock] | None to Optional[Tuple[Stock, Stock]]
    """Moves a quantity of seedlings from one stock entry to another location."""
    from_stock = get_stock_by_id(db, from_stock_id)
    if not from_stock or from_stock.quantity < quantity_to_move:
        return None

    existing_to_stock = db.query(Stock).filter(
        Stock.tree_type_id == from_stock.tree_type_id,
        Stock.location_id == to_location_id
    ).first()

    if existing_to_stock:
        existing_to_stock.quantity += quantity_to_move
        to_stock = existing_to_stock
    else:
        to_stock = Stock(
            tree_type_id=from_stock.tree_type_id,
            location_id=to_location_id,
            quantity=quantity_to_move,
            cost_per_seedling=from_stock.cost_per_seedling
        )
        db.add(to_stock)

    from_stock.quantity -= quantity_to_move
    db.commit()
    db.refresh(from_stock)
    db.refresh(to_stock)
    return from_stock, to_stock


# --- Transaction Operations (Sales Logic) ---

def record_sale(db: Session, tree_type_id: int, quantity_sold: int) -> Optional[Transaction]: # Changed Transaction | None to Optional[Transaction]
    """
    Records a sale and decrements stock.
    This implementation assumes stock can be decremented from any available batch
    or a single cumulative stock entry per tree type.
    For simplicity, we'll find all available stock of that type and decrement.
    """
    tree_type = get_tree_type_by_id(db, tree_type_id)
    if not tree_type:
        return None

    available_stock_entries = db.query(Stock).filter(
        Stock.tree_type_id == tree_type_id,
        Stock.quantity > 0
    ).order_by(Stock.date_added.asc()).all()

    total_available_quantity = sum(s.quantity for s in available_stock_entries)

    if total_available_quantity < quantity_sold:
        return None

    remaining_to_sell = quantity_sold
    for stock_entry in available_stock_entries:
        if remaining_to_sell <= 0:
            break
        if stock_entry.quantity >= remaining_to_sell:
            stock_entry.quantity -= remaining_to_sell
            remaining_to_sell = 0
        else:
            remaining_to_sell -= stock_entry.quantity
            stock_entry.quantity = 0
        db.add(stock_entry)

    unit_sale_price = tree_type.base_unit_price
    total_amount = unit_sale_price * quantity_sold

    db_transaction = Transaction(
        tree_type_id=tree_type_id,
        quantity_sold=quantity_sold,
        unit_sale_price_at_time_of_sale=unit_sale_price,
        total_amount=total_amount,
        transaction_date=datetime.datetime.now()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def get_all_transactions(db: Session, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> List[Transaction]: # Changed list[Transaction] to List[Transaction], added Optional for parameters
    """Retrieves all transactions, with optional date filters."""
    query = db.query(Transaction).order_by(Transaction.transaction_date.desc())
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date < end_date + datetime.timedelta(days=1))
    return query.all()