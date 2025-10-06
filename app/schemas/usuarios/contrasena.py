from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date

class ContrasenaBase(BaseModel):
    id_usuario: int = Field(..., description="ID del usuario dueño de la contraseña")
    fecha_cambio: date = Field(
        ..., description="Fecha en que se registró el cambio de contraseña"
    )
    hash_contrasena: str = Field(
        ..., min_length=1, description="Hash seguro de la contraseña"
    )
    estado: str = Field(
        ..., pattern="^(activa|inactiva)$", description="Estado de la contraseña"
    )

class ContrasenaCrear(ContrasenaBase):
    id_contrasena: int = Field(..., description="ID único de la contraseña")

class Contrasena(ContrasenaBase):
    id_contrasena: int = Field(..., description="ID único de la contraseña")
    model_config = ConfigDict(from_attributes=True)

class ContrasenaActualizar(BaseModel):
    fecha_cambio: Optional[date] = None
    hash_contrasena: Optional[str] = Field(
        None, min_length=1, description="Nuevo hash de la contraseña"
    )
    estado: Optional[str] = Field(
        None, pattern="^(activa|inactiva)$", description="Nuevo estado de la contraseña"
    )