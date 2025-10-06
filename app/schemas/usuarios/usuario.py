from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    apellido: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    telefono: str = Field(..., min_length=7, max_length=15)
    rol: str = Field(
        ...,
        description="Rol del usuario en el sistema",
        pattern="^(estudiante|docente|secretaria_academica)$"
    )

class UsuarioCrear(UsuarioBase):
    id_usuario: int = Field(..., description="Identificador único del usuario")

class Usuario(UsuarioBase):
    id_usuario: int = Field(..., description="Identificador único del usuario")
    model_config = ConfigDict(from_attributes=True)

class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, min_length=7, max_length=15)
    rol: Optional[str] = Field(
        None,
        pattern="^(estudiante|docente|secretaria_academica)$",
        description="Nuevo rol del usuario"
    )