from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models import OrderStatus

class OrderItemSchema(BaseModel):
    id: int
    product_id: int
    order_id: int
    quantity: int
    
    model_config = ConfigDict(from_attributes=True)

class OrderSchema(BaseModel):
    id: int
    status: OrderStatus
    created_at: datetime
    order_items: list[OrderItemSchema]

    model_config = ConfigDict(from_attributes=True)