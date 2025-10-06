from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.mysql import Base


class FacultadModel(Base):
    """
    Tabla de facultades de la universidad.
    """
    __tablename__ = "Facultad"

    id_facultad = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)

    # Relaciones
    unidades_academicas = relationship("UnidadAcademicaModel", back_populates="facultad")
    programas = relationship("ProgramaModel", back_populates="facultad")
    secretarias = relationship("SecretariaAcademicaModel", back_populates="facultad")