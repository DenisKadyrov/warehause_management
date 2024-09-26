# from app.crud.base import CRUDBase
from app.models import Order
from app.models.orders import (
     read_all,
     read_by_id, 
     create,
     update
)
from app.schemes.order import (
       CreateOrderRequest,
       UpdateOrderRequest,
)
from app.schemes.product import UpdateProductRequest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.schemes import base_schemes
from app.crud.product import get_product_by_id, update_product


async def create_order(
    session: AsyncSession, 
    order_in: CreateOrderRequest
) -> base_schemes.OrderSchema:
        for item in order_in.order_items:
               product = await get_product_by_id(
                      session=session, 
                      product_id=item.product_id
                )
               if item.quantity > product.quantity:
                      raise HTTPException(
                             status_code=404,
                             detail=f"Insufficient stock for product {product.name}. Available: {product.available_quantity}, requested: {item.quantity}"
                        )
               await update_product(
                      session=session,
                      id=product.id,
                      product_in=UpdateProductRequest(
                             name=product.name,
                             description=product.description,
                             price=product.price,
                             quantity=product.quantity - item.quantity
                      )
               )
        order = await create(
              session=session,
              order_items=order_in.order_items,
              status=order_in.status,
        )
    
        return base_schemes.OrderSchema.model_validate(order)

async def get_all_orders(session: AsyncSession):
        async for order in read_all(session):
            yield base_schemes.OrderSchema.model_validate(order)

async def get_order_by_id(
            session: AsyncSession, 
            order_id: int
) -> base_schemes.OrderSchema:
        order = await read_by_id(session=session, order_id=order_id)
        if not order:
              raise HTTPException(status_code=404)
        return base_schemes.OrderSchema.model_validate(order)

async def update_order(
            session: AsyncSession, 
            id: int,
            order_in: UpdateOrderRequest
) -> base_schemes.OrderSchema:
        order = await read_by_id(session=session, order_id=id)
        if not order:
               raise HTTPException(status_code=404)
        updated_order = await update(
                session=session,
                id=id,
                status=order_in.status
        )
        return base_schemes.OrderSchema.model_validate(updated_order)