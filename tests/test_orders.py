import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from .utils import ID_STRING, DATA

from app.models import Order, OrderItem, Product, OrderStatus
from app.crud import orders as order_crud


@pytest.mark.anyio
async def setup_data(session: AsyncSession) -> None:
    """
    Add test data to orders table in DB
    """
    order1 = Order(
        status=OrderStatus.in_progress,
    )
    order2 = Order(
        status=OrderStatus.delivered,
    )
    product1 = Product(name="Product1", description="desc", quantity=3, price=7.4)
    product2 = Product(name="Product2", description="desc", quantity=4, price=10.4)
    session.add_all([order1, order2, product1, product2])

    await session.flush()

    await session.refresh(order1)
    await session.refresh(order2)
    await session.refresh(product1)
    await session.refresh(product2)

    order_item1 = OrderItem(
        order_id=order1.id,
        product_id=product1.id,
        quantity=2,
    )
    order_item2 = OrderItem(
        order_id=order2.id,
        product_id=product2.id,
        quantity=1,
    )
    session.add_all([order_item2, order_item1])


    await session.flush()
    return product1.id


@pytest.mark.anyio
async def test_orders_read_all(ac: AsyncClient, session: AsyncSession) -> None:
    # setup 
    await setup_data(session)

    # execute
    response = await ac.get(
        "/orders/"
    )

    assert 200 == response.status_code
    expected = {
        "orders": [
            {
                "id": ID_STRING,
                "created_at": DATA,
                "status": "в процессе",
                "order_items": [
                    {
                        "id": ID_STRING,
                        "order_id": ID_STRING,
                        "product_id": ID_STRING,
                        "quantity": 2
                    },
                        
                ]
            },
                        {
                "id": ID_STRING,
                "status": "доставлен",
                "created_at": DATA,
                "order_items": [
                    {
                        "id": ID_STRING,
                        "order_id": ID_STRING,
                        "product_id": ID_STRING,
                        "quantity": 1
                    },
                        
                ]
            },
        ]
    }
    assert expected == response.json()

@pytest.mark.anyio
async def test_order_read(ac: AsyncClient, session: AsyncSession) -> None:
    # setup 
    await setup_data(session)

    product = [pd async for pd in order_crud.get_all_orders(session)][0]    
    # execute
    response = await ac.get(
        f"/orders/{product.id}"
    )

    assert 200 == response.status_code
    expected = {
                "id": ID_STRING,
                "created_at": DATA,
                "status": "в процессе",
                "order_items": [
                    {
                        "id": ID_STRING,
                        "order_id": ID_STRING,
                        "product_id": ID_STRING,
                        "quantity": 2
                    },
                ]
    }
    print(response.json())
    assert response.json() == expected


@pytest.mark.anyio
async def test_order_create(ac: AsyncClient, session: AsyncSession) -> None:
    # setup
    product_id = await setup_data(session)

    # execute
    response = await ac.post(
        "/orders/",
        json={
            "status": "отправлен",
            "order_items": [
                {
                    "product_id": product_id,
                    "quantity": 3
                },
            ]
        }
    )

    assert 200 == response.status_code
    expected = {
                "id": ID_STRING,
                "created_at": DATA,
                "status": "отправлен",
                "order_items": [
                    {
                        "id": ID_STRING,
                        "order_id": ID_STRING,
                        "product_id": product_id,
                        "quantity": 3
                    },
                ]
    }
    assert expected == response.json()


@pytest.mark.anyio
async def test_order_update(ac: AsyncClient, session: AsyncSession) -> None:
    # setup
    await setup_data(session)
    
    order = [p async for p in order_crud.get_all_orders(session)][0]

    # execute
    response = await ac.patch(
        f"/orders/{order.id}/status",
        json={
            "status": "доставлен",
        }
    )

    assert 200 == response.status_code
    expected = {
      
                "id": ID_STRING,
                "created_at": DATA,
                "status": "доставлен",
                "order_items": [
                    {
                        "id": ID_STRING,
                        "order_id": ID_STRING,
                        "product_id": ID_STRING,
                        "quantity": 2
                    },
                ]
                
    }
    assert expected == response.json()