from pydantic import BaseModel

from .order_item import OrderItem
from app.models import OrderStatus
from app.schemes import base_schemes


class BaseOrder(BaseModel):
    status: OrderStatus


class CreateOrderRequest(BaseOrder):
    order_items: list[OrderItem]


class CreateOrderResponse(base_schemes.OrderSchema):
    pass


class ReadOrderResponse(base_schemes.OrderSchema):
    pass


class ReadAllOrdersResponse(BaseModel):
    orders: list[base_schemes.OrderSchema]


class UpdateOrderRequest(BaseOrder):
    pass


class UpdateOrderResponse(base_schemes.OrderSchema):
    pass