
import enum

from datetime import datetime

from sqlalchemy import DateTime, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base
from .order_items import OrderItem, create_or
from app.schemes import order_item


class OrderStatus(enum.Enum):
    in_progress = "в процессе"
    sended = "отправлен"
    delivered = "доставлен"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(), 
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(nullable=False)

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", 
        back_populates="order",
        cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )

async def read_all(
        session: AsyncSession, 
        include_order_items: bool = True,
):
    """
    Function for read all orders from DB
    """
    stmt = select(Order)
    if include_order_items:
        stmt = stmt.options(selectinload(Order.order_items))

    stream = await session.stream_scalars(stmt.order_by(Order.id))
    async for row in stream:
        yield row

async def read_by_id(
    session: AsyncSession, 
    order_id: int,
    include_order_items: bool = True,
) -> Order:
    """
    Function for read a order from DB by id
    """
    stmt = select(Order).where(Order.id == order_id)
    if include_order_items:
        stmt = stmt.options(selectinload(Order.order_items))
    return await session.scalar(stmt.order_by(Order.id))

async def create(
    session: AsyncSession, 
    status: OrderStatus,
    order_items: list[order_item.OrderItem],
) -> Order:
    """
    Function for create Order.
    """
    order = Order(
        status=status,
    )
    session.add(order)

    await session.flush()
    await session.refresh(order)

    order_items_list = [await create_or(
        session=session, 
        product_id=i.product_id, 
        order_id=order.id, 
        quantity=i.quantity
    ) for i in order_items]
    

    session.add_all(order_items_list)
    await session.commit()
    await session.refresh(order)

    new = await read_by_id(session=session, order_id=order.id)
    

    return new

async def update(
        session: AsyncSession, 
        id: int, 
        status: OrderStatus,
) -> Order:
    """
    Function for update Order by id.
    It is return updated prouct.
    """
    order = await read_by_id(session=session, order_id=id)

    # update data
    order.status = status

    await session.commit()
    await session.refresh(order)

    return order