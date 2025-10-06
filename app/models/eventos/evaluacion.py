from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.mysql import Base
import enum


class EstadoEvaluacionEnum(str, enum.Enum):
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"


class EvaluacionModel(Base):
    """
    Evaluaciones realizadas por la Secretaría Académica sobre eventos.
    """
    __tablename__ = "Evaluacion"

    id_evaluacion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_evento = Column(Integer, ForeignKey("Evento.id_evento"))
    id_secretaria = Column(Integer, ForeignKey("SecretariaAcademica.id_usuario"))

    estado = Column(Enum(EstadoEvaluacionEnum), nullable=False)
    fecha_evaluacion = Column(Date, nullable=False)
    justificacion = Column(String(500), nullable=True)
    acta_aprobacion = Column(String(255), nullable=True)  # PDF del acta

    # Relaciones
    evento = relationship("EventoModel", back_populates="evaluaciones")
    secretaria = relationship("SecretariaAcademicaModel", back_populates="evaluaciones")
    notificaciones = relationship("NotificacionModel", back_populates="evaluacion", cascade="all, delete-orphan")
