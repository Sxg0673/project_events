from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.mysql import Base


class DocenteModel(Base):
    """
    Subtipo de Usuario para docentes.
    """
    __tablename__ = "Docente"

    id_usuario = Column(Integer, ForeignKey("Usuario.id_usuario"), primary_key=True)
    id_unidad_academica = Column(Integer, ForeignKey("UnidadAcademica.id_unidad_academica"), nullable=False)

    # Relaciones
    usuario = relationship("UsuarioModel", back_populates="docente")
    unidad_academica = relationship("UnidadAcademicaModel", back_populates="docentes")