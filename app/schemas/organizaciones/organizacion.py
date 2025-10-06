from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class OrganizacionBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    representante_legal: str = Field(..., min_length=1, max_length=100)
    telefono: str = Field(..., min_length=7, max_length=15)
    ubicacion: str = Field(..., min_length=1, max_length=200)
    sector_economico: str = Field(..., min_length=1, max_length=100)
    actividad_principal: str = Field(..., min_length=1, max_length=150)

class OrganizacionCrear(OrganizacionBase):
    id_organizacion: int = Field(..., description="ID de la organización")

class Organizacion(OrganizacionBase):
    id_organizacion: int = Field(..., description="ID de la organización")
    
    model_config = ConfigDict(from_attributes=True)

class OrganizacionActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    representante_legal: Optional[str] = Field(None, min_length=1, max_length=100)
    telefono: Optional[str] = Field(None, min_length=7, max_length=15)
    ubicacion: Optional[str] = Field(None, min_length=1, max_length=200)
    sector_economico: Optional[str] = Field(None, min_length=1, max_length=100)
    actividad_principal: Optional[str] = Field(None, min_length=1, max_length=150)