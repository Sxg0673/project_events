# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    # --- Base de datos ---
    DATABASE_URL: str = Field(
        ...,
        description= "URL de conexión a MySQL (ej: mysql+aiomysql://user:pass@host:3306/dbname)" # Remplazar
    )
    DEBUG: bool = Field(
        default=False,
        description="Activa el modo debug de SQLAlchemy (echo=True)"
    )

    # --- App / OpenAPI ---
    APP_NAME: str = Field(
        default="Eventos U - API",
        description="Nombre de la aplicación"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Versión de la aplicación"
    )
    ALLOWED_ORIGINS: List[str] = Field(
        default=["*"],
        description="Orígenes permitidos para CORS"
    )

settings = Settings()  # type: ignore
