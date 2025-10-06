from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.mysql import Base


class UsuarioModel(Base):
    """
    Tabla base de usuarios (común a estudiantes, docentes y secretarias académicas).
    """
    __tablename__ = "Usuario"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=False)  # cédula
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20), nullable=True)

    # Relaciones hacia las tablas hijas
    estudiante = relationship("EstudianteModel", back_populates="usuario", uselist=False)
    docente = relationship("DocenteModel", back_populates="usuario", uselist=False)
    secretaria = relationship("SecretariaAcademicaModel", back_populates="usuario", uselist=False)

    # Relaciones con eventos
    eventos_responsables = relationship("EventoResponsableModel", back_populates="usuario")

    # Relacion con credenciales
    credenciales = relationship("CredencialModel", back_populates="usuario", cascade="all, delete-orphan")

    # Relacion con notificaciones
    notificaciones = relationship("NotificacionModel", back_populates="usuario", cascade="all, delete-orphan")