import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from .utils import ID_STRING

from app.models import Product
from app.crud import product as product_crud


@pytest.mark.anyio
async def setup_data(session: AsyncSession) -> None:
    """
    Add test data to products table in DB
    """
    product1 = Product(name="Product1", description="desc", quantity=3, price=7.4)
    product2 = Product(name="Product2", description="desc", quantity=4, price=10.4)
    session.add_all([product1, product2])

    await session.flush()

    await session.commit()

@pytest.mark.anyio
async def test_products_read_all(ac: AsyncClient, session: AsyncSession) -> None:
    # setup 
    await setup_data(session)

    # execute
    response = await ac.get(
        "/products/"
    )

    assert 200 == response.status_code
    expected = {
        "products": [
            {
                "id": ID_STRING,
                "name": "Product1",
                "description": "desc",
                "price": 7.4,
                "quantity": 3,
            },
            {
                "id": ID_STRING,
                "name": "Product2",
                "description": "desc",
                "price": 10.4,
                "quantity": 4,
            }
        ]
    }
    assert response.json() == expected

@pytest.mark.anyio
async def test_product_read(ac: AsyncClient, session: AsyncSession) -> None:
    # setup 
    await setup_data(session)

    product = [pd async for pd in product_crud.get_all_products(session)][0]    
    # execute
    response = await ac.get(
        f"/products/{product.id}"
    )

    assert 200 == response.status_code
    expected = {
                "id": product.id,
                "name": "Product1",
                "description": "desc",
                "price": 7.4,
                "quantity": 3,
    }
    print(response.json())
    assert response.json() == expected


@pytest.mark.anyio
async def test_product_create(ac: AsyncClient, session: AsyncSession) -> None:
    # execute
    response = await ac.post(
        "/products/",
        json={
            "name": "Product",
            "description": "d",
            "quantity": 9,
            "price": 5.6
        }
    )

    assert 200 == response.status_code
    expected = {
      
                "id": ID_STRING,
                "name": "Product",
                "description": "d",
                "price": 5.6,
                "quantity": 9,
    }
    assert expected == response.json()


@pytest.mark.anyio
async def test_product_update(ac: AsyncClient, session: AsyncSession) -> None:
    # setup
    await setup_data(session)
    
    product = [p async for p in product_crud.get_all_products(session)][0]

    assert product.name == "Product1"
    # execute
    response = await ac.put(
        f"/products/{product.id}",
        json={
            "name": "Product",
            "description": "Any desc",
            "quantity": 9,
            "price": 5.6
        }
    )

    assert 200 == response.status_code
    expected = {
      
                "id": ID_STRING,
                "name": "Product",
                "description": "Any desc",
                "price": 5.6,
                "quantity": 9,
    }
    assert expected == response.json()

@pytest.mark.anyio
async def test_product_delete(ac: AsyncClient, session: AsyncSession) -> None:
    # setup
    await setup_data(session)
    
    product = [p async for p in product_crud.get_all_products(session)][0]

    assert product.name == "Product1"
    # execute
    response = await ac.delete(
        f"/products/{product.id}",
    )

    assert 200 == response.status_code
    expected = {
        "Delete": "Successfull"
    }
    assert expected == response.json()