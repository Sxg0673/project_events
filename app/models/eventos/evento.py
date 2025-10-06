from sqlalchemy import Column, Integer, String, Enum, Date, Time
from sqlalchemy.orm import relationship
from app.db.mysql import Base
import enum


class TipoEventoEnum(str, enum.Enum):
    LUDICO = "ludico"
    ACADEMICO = "academico"


class EstadoEventoEnum(str, enum.Enum):
    REGISTRADO = "registrado"
    EN_REVISION = "en_revision"
    APROBADO = "aprobado"


class EventoModel(Base):
    """
    Modelo de base de datos para eventos académicos y lúdicos.
    """
    __tablename__ = "Evento"

    id_evento = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)

    tipo = Column(Enum(TipoEventoEnum), nullable=False)
    estado = Column(Enum(EstadoEventoEnum), default=EstadoEventoEnum.REGISTRADO)

    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)

    # Relaciones
    responsables = relationship(
        "EventoResponsableModel",
        back_populates="evento",
        cascade="all, delete-orphan"
    )

    instalaciones = relationship(
        "InstalacionEventoModel",
        back_populates="evento",
        cascade="all, delete-orphan"
    )

    organizaciones = relationship(
        "RepresentanteModel",
        back_populates="evento",
        cascade="all, delete-orphan"
    )

    evaluaciones = relationship(
        "EvaluacionModel",
        back_populates="evento",
        cascade="all, delete-orphan"
    )
