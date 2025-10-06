from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.mysql import Base


class InstalacionEventoModel(Base):
    """
    Tabla intermedia para asociar eventos con instalaciones.
    """
    __tablename__ = "InstalacionEvento"

    id_evento = Column(Integer, ForeignKey("Evento.id_evento"), primary_key=True)
    id_instalacion = Column(Integer, ForeignKey("Instalacion.id_instalacion"), primary_key=True)

    # Relaciones
    evento = relationship("EventoModel", back_populates="instalaciones")
    instalacion = relationship("InstalacionModel", back_populates="eventos")