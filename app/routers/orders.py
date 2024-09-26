from typing import Annotated
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import  AsyncSession

from app.schemes.order import (
    ReadAllOrdersResponse,
    ReadOrderResponse,
    CreateOrderRequest,
    CreateOrderResponse,
    UpdateOrderRequest,
    UpdateOrderResponse
)
from app.schemes import base_schemes
from app.crud import orders as order_crud
from app.database import get_db_session

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]



@router.post("/", response_model=Annotated[CreateOrderResponse, dict])
async def create_order(
    session: DBSessionDep,
    order_in: CreateOrderRequest,
) -> base_schemes.OrderSchema:
    try:
        order = await order_crud.create_order(session=session, order_in=order_in)
    except:
        {"Filed": "Can't create order"}
    return order

@router.get("/")
async def get_orders(session: DBSessionDep) -> Annotated[ReadAllOrdersResponse, dict]:
    try:
        return ReadAllOrdersResponse(orders=[p async for p in order_crud.get_all_orders(session=session)])
    except:
        return {"Filed": "Can't get orders"}


@router.get("/{id}", response_model=Annotated[ReadOrderResponse, dict])
async def get_order(
    session: DBSessionDep,
    id: int,
) -> base_schemes.OrderSchema:
    try:
        order = await order_crud.get_order_by_id(session=session, order_id=id)
    except:
        return {"Filed": "Can't get order by id"}
    return order

@router.patch("/{id}/status")
async def update_order(
    session: DBSessionDep,
    id: int,
    order_in: UpdateOrderRequest
) -> Annotated[UpdateOrderResponse, dict]:
    try:
        order = await order_crud.update_order(
            session=session, 
            id=id, 
            order_in=order_in
        )
    except:
        return {"Filed": "Can't update order"}
    return order
