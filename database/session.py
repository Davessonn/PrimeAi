from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config.settings import settings
from database.models import Base


database_url = make_url(settings.DATABASE_URL)
if database_url.drivername in ("postgres", "postgresql"):
    database_url = database_url.set(drivername="postgresql+asyncpg")

engine = create_async_engine(database_url, pool_pre_ping=True)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    if database_url.host and any(char in database_url.host for char in "@/?#"):
        raise ValueError(
            "Invalid DATABASE_URL hostname. Percent-encode special characters "
            "in the username and password (for example, @ as %40)."
        )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
