from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.mysql import Base


class OrganizacionExternaModel(Base):
    """
    Tabla de organizaciones externas que pueden participar en eventos.
    """
    __tablename__ = "OrganizacionExterna"

    id_organizacion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    representante_legal = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    ubicacion = Column(String(200), nullable=False)
    sector_economico = Column(String(100), nullable=True)
    actividad_principal = Column(String(200), nullable=True)

    # Relación con eventos
    eventos = relationship("RepresentanteModel", back_populates="organizacion")