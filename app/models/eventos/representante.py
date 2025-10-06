from sqlalchemy import Column, Integer, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from app.db.mysql import Base


class RepresentanteModel(Base):
    """
    Tabla intermedia para registrar la participación de organizaciones externas en eventos.
    """
    __tablename__ = "Representante"

    id_evento = Column(Integer, ForeignKey("Evento.id_evento"), primary_key=True)
    id_organizacion = Column(Integer, ForeignKey("OrganizacionExterna.id_organizacion"), primary_key=True)

    # Atributos adicionales
    es_legal = Column(Boolean, default=True)  # True si es el representante legal
    certificado_participacion = Column(String(255), nullable=True)  # Ruta o nombre del archivo PDF

    # Relaciones
    evento = relationship("EventoModel", back_populates="organizaciones")
    organizacion = relationship("OrganizacionExternaModel", back_populates="eventos")