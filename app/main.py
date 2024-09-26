import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import sessionmanager

from app.routers import products, orders
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan)


app.include_router(orders.router)
app.include_router(products.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        host=settings.run.HOST,
        port=settings.run.PORT,
    )