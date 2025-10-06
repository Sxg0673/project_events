from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.mysql import Base


class SecretariaAcademicaModel(Base):
    """
    Subtipo de Usuario para secretarios académicos.
    """
    __tablename__ = "SecretariaAcademica"

    id_usuario = Column(Integer, ForeignKey("Usuario.id_usuario"), primary_key=True)
    id_facultad = Column(Integer, ForeignKey("Facultad.id_facultad"), nullable=False)

    # Relaciones
    usuario = relationship("UsuarioModel", back_populates="secretaria")
    facultad = relationship("FacultadModel", back_populates="secretarias")

    evaluaciones = relationship("EvaluacionModel", back_populates="secretaria")