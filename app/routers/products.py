from typing import Annotated
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import  AsyncSession

from app.schemes.product import (
    ReadAllProductsResponse,
    ReadProductResponse,
    CreateProductRequest,
    CreateProductResponse,
    UpdateProductRequest,
    UpdateProductResponse
)
from app.crud import product as product_crud
from app.database import get_db_session

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]



@router.post("/")
async def create_product(
    session: DBSessionDep,
    product_in: CreateProductRequest,
) -> CreateProductResponse:
    try:
        product = await product_crud.create_product(session=session, product_in=product_in)
    except:
        return {"Filed": "Not correct data"}
    return product

@router.get("/")
async def get_products(session: DBSessionDep) -> ReadAllProductsResponse:
    try:
        return ReadAllProductsResponse(products=[p async for p in product_crud.get_all_products(session=session)])
    except:
        return {"Filed": "Can't get products"}


@router.get("/{id}")
async def get_product(
    session: DBSessionDep,
    id: int,
) -> ReadProductResponse:
    try:
        product = await product_crud.get_product_by_id(session=session, product_id=id)
    except:
        return {"Filed": "Can't get product by id"}
    return product

@router.put("/{id}")
async def update_product(
    session: DBSessionDep,
    id: int,
    update_product: UpdateProductRequest
) -> UpdateProductResponse:
    try:
        product = await product_crud.update_product(
            session=session, 
            id=id, 
            product_in=update_product
        )
    except:
        return {"Filed": "Can't update product, may be not correct data"}
    return product

@router.delete("/{id}")
async def delete_product(
    session: DBSessionDep,
    id: int,
):
    try:
        return await product_crud.delete_product(session=session, product_id=id)
    except:
        return {"Filed": "Can'n delete product"}