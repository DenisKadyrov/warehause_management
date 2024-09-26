from pydantic import BaseModel


class OrderItem(BaseModel):
    product_id: int
    quantity: int


class OrderItemWithId(OrderItem):
    id: int
    order_id: int
