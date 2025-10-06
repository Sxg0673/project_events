# app/db/mysql.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# 1) Motor asíncrono (MySQL con aiomysql). 
#    - echo usa settings.DEBUG para log de SQL
#    - pool_pre_ping evita "MySQL server has gone away"
#    - pool_recycle renueva conexiones inactivas
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,        # ej: "mysql+aiomysql://user:pass@localhost:3306/mi_db" REMPLAZAR
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=1800,            # segundos
    future=True,
)

# 2) Session factory asíncrona
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,       # evita expirar objetos tras commit (útil para respuestas API)
)

# 3) Base declarativa para todos los modelos ORM
Base = declarative_base()

# 4) Dependencia de FastAPI: una sesión por request
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Devuelve una sesión asíncrona por petición y la cierra automáticamente.
    Uso típico en rutas:
        async def endpoint(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session
