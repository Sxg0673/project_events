from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class SecretariaAcademicaBase(BaseModel):
    id_facultad: int = Field(
        ..., description="ID de la facultad a la que pertenece el secretario académico"
    )

class SecretariaAcademicaCrear(SecretariaAcademicaBase):
    id_usuario: int = Field(..., description="ID del usuario asociado")

class SecretariaAcademica(SecretariaAcademicaBase):
    id_usuario: int = Field(..., description="ID del usuario asociado")
    
    model_config = ConfigDict(from_attributes=True)

class SecretariaAcademicaActualizar(BaseModel):
    id_facultad: Optional[int] = Field(
        None, description="Nueva facultad asignada al secretario académico"
    )