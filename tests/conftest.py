from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, SessionTransaction

from app.database import get_db_session, get_db_url
from app.models import Base
from app.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def ac() -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture(scope="session")
def setup_db() -> Generator:
    engine = create_engine(f"{get_db_url().replace('+asyncpg', '')}")
    conn = engine.connect()
    # Terminate transaction
    conn.execute(text("commit"))
    try:
        conn.execute(text("drop database test"))
    except SQLAlchemyError:
        pass
    finally:
        conn.close()

    conn = engine.connect()
    # Terminate transaction
    conn.execute(text("commit"))
    conn.execute(text("create database test"))
    conn.close()

    yield

    conn = engine.connect()
    # Terminate transaction
    conn.execute(text("commit"))
    try:
        conn.execute(text("drop database test"))
    except SQLAlchemyError:
        pass
    conn.close()
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db(setup_db: Generator) -> Generator:
    engine = create_engine(f"{get_db_url().replace('+asyncpg', '')}")

    with engine.begin():
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        yield
        Base.metadata.drop_all(engine)

    engine.dispose()


@pytest.fixture
async def session() -> AsyncGenerator:
    # https://github.com/sqlalchemy/sqlalchemy/issues/5811#issuecomment-756269881
    async_engine = create_async_engine(f"{get_db_url()}")
    async with async_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()
        AsyncSessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=conn,
            future=True,
        )

        async_session = AsyncSessionLocal()

        # Event listener to restart nested transactions after each one ends
        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def restart_nested_transaction(session: Session, transaction: SessionTransaction) -> None:
            if conn.closed:
                return
            if not conn.in_nested_transaction():
                conn.sync_connection.begin_nested()

        # Override the `get_db_session` dependency to use the test session
        async def override_get_db_session() -> AsyncGenerator:
            try:
                yield async_session
            finally:
                await async_session.rollback()

        # Set the app's session override
        app.dependency_overrides[get_db_session] = override_get_db_session

        yield async_session

        await async_session.close()

    # Dispose of the engine after the test
    await async_engine.dispose()

    # Close all sessions to avoid leaks
    # close_all_sessions()
