from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import enum

Base = declarative_base()

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)
    item_id = Column(Integer, index=True)
    quantity = Column(Integer)
    total_price = Column(Float)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    shipping_address = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)