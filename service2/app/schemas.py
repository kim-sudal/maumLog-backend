from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import OrderStatus

class OrderBase(BaseModel):
    customer_id: int
    item_id: int
    quantity: int
    total_price: float
    shipping_address: str
    status: OrderStatus = OrderStatus.PENDING

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    quantity: Optional[int] = None
    total_price: Optional[float] = None
    shipping_address: Optional[str] = None
    status: Optional[OrderStatus] = None

class Order(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True