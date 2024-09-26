# from app.crud.base import CRUDBase
from app.models import Product
from app.models.products import (
     read_all,
     read_by_id, 
     create,
     delete,
     update
)
from app.schemes.product import (
       CreateProductRequest,
       CreateProductResponse,
       ReadProductResponse,
       UpdateProductRequest,
       UpdateProductResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


async def create_product(
    session: AsyncSession, 
    product_in: CreateProductRequest
) -> CreateProductResponse:
        product = await create(
              session=session,
              **product_in.__dict__
        )
        return CreateProductResponse(**product.__dict__)

async def get_all_products(session: AsyncSession):
        async for product in read_all(session):
            yield ReadProductResponse(**product.__dict__)

async def get_product_by_id(
            session: AsyncSession, 
            product_id: int
) -> ReadProductResponse:
        product = await read_by_id(session=session, product_id=product_id)
        if not product:
              raise HTTPException(status_code=404)
        return ReadProductResponse(**product.__dict__)

async def update_product(
            session: AsyncSession, 
            id: int,
            product_in: UpdateProductRequest,
) -> UpdateProductResponse:
        product = await read_by_id(session=session, product_id=id)
        if not product:
               raise HTTPException(status_code=404)
        updated_product = await update(
                session=session,
                id=id,
                **product_in.model_dump()
        )
        return UpdateProductResponse(**updated_product.__dict__)
    
async def delete_product(
              session: AsyncSession,
              product_id: int
):
        product = await read_by_id(session=session, product_id=product_id)
        if not product:
               return
        await delete(session=session, product=product)
        return {"Delete": "Successfull"}