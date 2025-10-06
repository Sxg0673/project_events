from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.mysql import Base
import enum
from datetime import datetime


class EstadoCredencialEnum(str, enum.Enum):
    VIGENTE = "activa"
    EXPIRADA = "inactiva"


class CredencialModel(Base):
    """
    Histórico de credenciales de usuario.
    Un usuario puede tener varias contraseñas a lo largo del tiempo,
    pero solo una estará vigente.
    """
    __tablename__ = "Credencial"

    id_credencial = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("Usuario.id_usuario"), nullable=False)

    hash_password = Column(String(255), nullable=False)  # Contraseña encriptada
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    estado = Column(Enum(EstadoCredencialEnum), default=EstadoCredencialEnum.VIGENTE)

    # Relación con usuario
    usuario = relationship("UsuarioModel", back_populates="credenciales")