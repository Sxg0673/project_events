from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import date, time
from enum import Enum


class TipoEventoEnum(str, Enum):
    LUDICO = "ludico"
    ACADEMICO = "academico"


class EstadoEventoEnum(str, Enum):
    REGISTRADO = "registrado"
    EN_REVISION = "en_revision"
    APROBADO = "aprobado"


class EventoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre del evento")
    descripcion: Optional[str] = Field(None, max_length=500)
    tipo: TipoEventoEnum = Field(..., description="Tipo de evento: académico o lúdico")

    fecha_inicio: date = Field(..., description="Fecha de inicio del evento")
    fecha_fin: date = Field(..., description="Fecha de finalización del evento")

    hora_inicio: time = Field(..., description="Hora de inicio")
    hora_fin: time = Field(..., description="Hora de finalización")

    @field_validator("fecha_fin")
    @classmethod
    def validar_rango_fechas(cls, v, values):
        fecha_inicio = values.get("fecha_inicio")
        if fecha_inicio and v < fecha_inicio:
            raise ValueError("La fecha_fin no puede ser anterior a fecha_inicio")
        return v

    @field_validator("hora_fin")
    @classmethod
    def validar_rango_horas(cls, v, values):
        hora_inicio = values.get("hora_inicio")
        if hora_inicio and v <= hora_inicio:
            raise ValueError("La hora_fin debe ser mayor que hora_inicio")
        return v


class EventoCrear(EventoBase):
    estado: Optional[EstadoEventoEnum] = EstadoEventoEnum.REGISTRADO


class Evento(EventoBase):
    id_evento: int = Field(..., alias="id_evento")
    estado: EstadoEventoEnum

    model_config = ConfigDict(from_attributes=True)