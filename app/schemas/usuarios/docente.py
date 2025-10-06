from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class DocenteBase(BaseModel):
    id_unidad_academica: int = Field(
        ..., description="ID de la unidad académica a la que pertenece el docente"
    )

class DocenteCrear(DocenteBase):
    id_usuario: int = Field(..., description="ID del usuario asociado")

class Docente(DocenteBase):
    id_usuario: int = Field(..., description="ID del usuario asociado")
    
    model_config = ConfigDict(from_attributes=True)

class DocenteActualizar(BaseModel):
    id_unidad_academica: Optional[int] = Field(
        None, description="Nueva unidad académica del docente"
    )