from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class RepresentanteBase(BaseModel):
    id_evento: int = Field(..., description="ID del evento asociado")
    id_organizacion: int = Field(..., description="ID de la organización externa asociada")
    nombre_representante: str = Field(
        ..., description="Nombre del representante asignado al evento", min_length=1, max_length=100
    )
    representante_legal: str = Field(
        ..., description="Indica si es el representante legal", pattern="^(Si|No)$"
    )
    certificado_participacion: Optional[bytes] = Field(
        None, description="Archivo PDF firmado por el representante legal"
    )

class RepresentanteCrear(RepresentanteBase):
    pass

class Representante(RepresentanteBase):
    model_config = ConfigDict(from_attributes=True)

class RepresentanteActualizar(BaseModel):
    nombre_representante: Optional[str] = None
    representante_legal: Optional[str] = Field(
        None, pattern="^(Si|No)$", description="Actualizar si es representante legal"
    )
    certificado_participacion: Optional[bytes] = None