from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.mysql import Base


class UnidadAcademicaModel(Base):
    """
    Tabla de unidades académicas de una facultad.
    """
    __tablename__ = "UnidadAcademica"

    id_unidad_academica = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)

    id_facultad = Column(Integer, ForeignKey("Facultad.id_facultad"))

    # Relaciones
    facultad = relationship("FacultadModel", back_populates="unidades_academicas")
    docentes = relationship("DocenteModel", back_populates="unidad_academica")