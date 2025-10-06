from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.mysql import Base


class EventoResponsableModel(Base):
    """
    Tabla intermedia para asignar responsables (docentes/estudiantes) a eventos.
    Un evento puede tener varios responsables y un usuario puede estar en varios eventos.
    """
    __tablename__ = "EventoResponsable"

    id_evento = Column(Integer, ForeignKey("Evento.id_evento"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("Usuario.id_usuario"), primary_key=True)

    # Ejemplo de atributo adicional
    fecha_asignacion = Column(Date, nullable=False)

    # Relaciones
    evento = relationship("EventoModel", back_populates="responsables")
    usuario = relationship("UsuarioModel", back_populates="eventos_responsables")