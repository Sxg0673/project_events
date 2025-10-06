from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class EstudianteBase(BaseModel):
    id_programa: int = Field(..., description="ID del programa académico al que pertenece el estudiante")

class EstudianteCrear(EstudianteBase):
    id_usuario: int = Field(..., description="ID del usuario asociado")

class Estudiante(EstudianteBase):
    id_usuario: int = Field(..., description="ID del usuario asociado")
    
    model_config = ConfigDict(from_attributes=True)

class EstudianteActualizar(BaseModel):
    id_programa: Optional[int] = Field(
        None, description="Nuevo programa académico del estudiante"
    )