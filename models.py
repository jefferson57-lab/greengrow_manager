

import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from typing import List, Optional # Added for consistency, though not strictly required by this file's current methods.

class TreeType(Base):
    __tablename__ = 'tree_types'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    base_unit_price = Column(Float, nullable=False)

    stocks = relationship("Stock", back_populates="tree_type")
    transactions = relationship("Transaction", back_populates="tree_type")

    def __repr__(self):
        return f"<TreeType(id={self.id}, name='{self.name}', price={self.base_unit_price})>"

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    stocks = relationship("Stock", back_populates="location")

    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}')>"

class Stock(Base):
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True, index=True)
    tree_type_id = Column(Integer, ForeignKey('tree_types.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    date_added = Column(DateTime, default=datetime.datetime.now)
    cost_per_seedling = Column(Float, default=0.0)

    tree_type = relationship("TreeType", back_populates="stocks")
    location = relationship("Location", back_populates="stocks")

    def __repr__(self):
        return (f"<Stock(id={self.id}, type_id={self.tree_type_id}, "
                f"location_id={self.location_id}, quantity={self.quantity})>")

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    tree_type_id = Column(Integer, ForeignKey('tree_types.id'), nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    unit_sale_price_at_time_of_sale = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, default=datetime.datetime.now)

    tree_type = relationship("TreeType", back_populates="transactions")

    def __repr__(self):
        return (f"<Transaction(id={self.id}, type_id={self.tree_type_id}, "
                f"sold={self.quantity_sold}, total={self.total_amount})>")