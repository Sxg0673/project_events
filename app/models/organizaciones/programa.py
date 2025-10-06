from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.mysql import Base


class ProgramaModel(Base):
    """
    Tabla de programas académicos de una facultad.
    """
    __tablename__ = "Programa"

    id_programa = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)

    id_facultad = Column(Integer, ForeignKey("Facultad.id_facultad"))

    # Relaciones
    facultad = relationship("FacultadModel", back_populates="programas")
    estudiantes = relationship("EstudianteModel", back_populates="programa")