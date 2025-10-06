from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class NotificacionBase(BaseModel):
    id_evaluacion: int = Field(..., description="ID de la evaluación asociada")
    id_usuario: int = Field(..., description="ID del usuario que recibe la notificación")
    mensaje: str = Field(..., min_length=1, max_length=500)
    fecha_envio: datetime = Field(..., description="Fecha en que se generó la notificación")

class NotificacionCrear(NotificacionBase):
    pass

class Notificacion(NotificacionBase):
    id_notificacion: int = Field(..., description="ID único de la notificación")
    
    model_config = ConfigDict(from_attributes=True)

class NotificacionActualizar(BaseModel):
    mensaje: str | None = Field(
        None, min_length=1, max_length=500, description="Nuevo contenido del mensaje"
    )
