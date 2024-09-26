from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base


if TYPE_CHECKING:
    from .products import Product
    from .orders import Order

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(nullable=False)

    order: Mapped["Order"] = relationship(
        "Order", 
        back_populates="order_items",
    )
    product: Mapped["Product"] = relationship(
        "Product", 
        back_populates="order_products",
    )


async def create_or(
    session: AsyncSession, 
    order_id: int,
    product_id: int,
    quantity: int
) -> OrderItem:
    """
    Function for create product.
    """
    order_item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
    )
    session.add(order_item)
    
    await session.commit()
    await session.refresh(order_item)

    return order_item
