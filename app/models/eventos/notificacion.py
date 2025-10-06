from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.mysql import Base
import enum
from datetime import datetime


class EstadoNotificacionEnum(str, enum.Enum):
    PENDIENTE = "pendiente"
    ENVIADO = "enviado"


class NotificacionModel(Base):
    """
    Notificaciones que informan a los responsables de eventos sobre el resultado de evaluaciones.
    """
    __tablename__ = "Notificacion"

    id_notificacion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_evaluacion = Column(Integer, ForeignKey("Evaluacion.id_evaluacion"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("Usuario.id_usuario"), nullable=False)

    mensaje = Column(String(500), nullable=False)
    estado = Column(Enum(EstadoNotificacionEnum), default=EstadoNotificacionEnum.PENDIENTE)
    fecha_envio = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    evaluacion = relationship("EvaluacionModel", back_populates="notificaciones")
    usuario = relationship("UsuarioModel", back_populates="notificaciones")