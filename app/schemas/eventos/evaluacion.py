from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import date

class EstadoEvaluacionEnum(str):
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"

class EvaluacionBase(BaseModel):
    id_evento: int = Field(..., description="ID del evento evaluado")
    id_secretaria: int = Field(..., description="ID del secretario académico que evalúa")
    estado: str = Field(..., pattern="^(aprobado|rechazado)$")
    fecha_evaluacion: date = Field(..., description="Fecha en la que se realizó la evaluación")
    justificacion: Optional[str] = Field(None, description="Motivo cuando el evento es rechazado")
    acta_aprobacion: Optional[bytes] = Field(None, description="PDF cuando el evento es aprobado")

    @field_validator("justificacion")
    @classmethod
    def validar_justificacion(cls, v, info):
        estado = info.data.get("estado")
        if estado == "rechazado" and (v is None or v.strip() == ""):
            raise ValueError("La justificación es obligatoria cuando el estado es 'rechazado'")
        return v

    @field_validator("acta_aprobacion")
    @classmethod
    def validar_acta(cls, v, info):
        estado = info.data.get("estado")
        if estado == "aprobado" and v is None:
            raise ValueError("El acta de aprobación es obligatoria cuando el estado es 'aprobado'")
        return v

class EvaluacionCrear(EvaluacionBase):
    pass

class Evaluacion(EvaluacionBase):
    id_evaluacion: int = Field(..., description="Identificador único de la evaluación")
    model_config = ConfigDict(from_attributes=True)

class EvaluacionActualizar(BaseModel):
    estado: Optional[str] = Field(None, pattern="^(aprobado|rechazado)$")
    justificacion: Optional[str] = None
    acta_aprobacion: Optional[bytes] = None

    @field_validator("justificacion")
    @classmethod
    def validar_justificacion_actualizar(cls, v, info):
        estado = info.data.get("estado")
        if estado == "rechazado" and (v is None or v.strip() == ""):
            raise ValueError("La justificación es obligatoria cuando el estado es 'rechazado'")
        return v

    @field_validator("acta_aprobacion")
    @classmethod
    def validar_acta_actualizar(cls, v, info):
        estado = info.data.get("estado")
        if estado == "aprobado" and v is None:
            raise ValueError("El acta es obligatoria cuando el estado es 'aprobado'")
        return v
