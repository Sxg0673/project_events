from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.mysql import Base


class EstudianteModel(Base):
    """
    Subtipo de Usuario para estudiantes.
    """
    __tablename__ = "Estudiante"

    id_usuario = Column(Integer, ForeignKey("Usuario.id_usuario"), primary_key=True)
    id_programa = Column(Integer, ForeignKey("Programa.id_programa"), nullable=False)

    # Relaciones
    usuario = relationship("UsuarioModel", back_populates="estudiante")
    programa = relationship("ProgramaModel", back_populates="estudiantes")