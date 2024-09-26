from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from typing import TYPE_CHECKING 

from . import Base, OrderItem
if TYPE_CHECKING:
    from app.models.order_items import OrderItem

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    order_products: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", 
        back_populates="product", 
        cascade="all,delete",
    )


async def read_all(session: AsyncSession):
    """
    Function for read all pdocucts from DB
    """
    stmt = select(Product)
    stream = await session.stream_scalars(stmt.order_by(Product.id))
    async for row in stream:
        yield row

async def read_by_id(
    session: AsyncSession, 
    product_id: int,
) -> Product:
    """
    Function for read a product from DB by id
    """
    stmt = select(Product).where(Product.id == product_id)
    return await session.scalar(stmt.order_by(Product.id))

async def create(
    session: AsyncSession, 
    name: str,
    description: str,
    price: float,
    quantity: int,
) -> Product:
    """
    Function for create product.
    """
    product = Product(
        name=name,
        description=description,
        price=price,
        quantity=quantity,
    )
    session.add(product)
    
    await session.commit()
    await session.refresh(product)


    # To fetch product
    new = await read_by_id(session, product.id)
    if not new:
        raise RuntimeError()
    return new

async def update(
        session: AsyncSession, 
        id: int, 
        name: str,
        description: str,
        price: float,
        quantity: int,
) -> Product:
    """
    Function for update product by id.
    It is return updated prouct.
    """
    stmt = select(Product).where(Product.id == id)
    product = await read_by_id(session=session, product_id=id)

    # update data
    product.name = name
    product.description = description
    product.price = price
    product.quantity = quantity

    await session.commit()
    await session.refresh(product)

    return product

async def delete(session: AsyncSession, product: Product) -> None:
    """
    Function for delete product.
    It receive an instance of the Product model and deleted it.
    """ 
    await session.delete(product)
    await session.commit()