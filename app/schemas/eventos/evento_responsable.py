from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date
from typing import Optional

class EventoResponsableBase(BaseModel):
    id_evento: int = Field(..., description="ID del evento asociado")
    cedula: int = Field(..., description="Cédula del responsable del evento")
    fecha_asignacion: date = Field(..., description="Fecha en que se asignó el rol de responsable")

    @field_validator('fecha_asignacion')
    @classmethod
    def validar_fecha_asignacion(cls, v):
        """Valida que la fecha de asignación no sea futura."""
        if v > date.today():
            raise ValueError("La fecha de asignación no puede ser futura")
        return v

class EventoResponsableCrear(EventoResponsableBase):
    pass

class EventoResponsable(EventoResponsableBase):
    model_config = ConfigDict(from_attributes=True)

class EventoResponsableActualizar(BaseModel):
    fecha_asignacion: Optional[date] = None

    @field_validator('fecha_asignacion')
    @classmethod
    def validar_actualizacion_fecha(cls, v):
        """Valida que la fecha de actualización no sea futura."""
        if v and v > date.today():
            raise ValueError("La fecha de asignación no puede ser futura")
        return v