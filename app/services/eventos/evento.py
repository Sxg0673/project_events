# app/services/eventos/evento_service.py
from datetime import datetime, time, date
from typing import Optional, Sequence, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.eventos.evento import EventoModel, EstadoEventoEnum, TipoEventoEnum
from app.models.usuarios.usuario import UsuarioModel
from app.crud.eventos.evento import (
    crear_evento as crud_crear_evento,
    listar_eventos as crud_listar_eventos,          # si tu CRUD 2 no trae filtros, igual lo exponemos
    buscar_evento_por_id as crud_buscar_evento_por_id,
    actualizar_evento as crud_actualizar_evento,
    eliminar_evento as crud_eliminar_evento,
)

# -----------------------------
# Utilidades de validación
# -----------------------------
def _validar_fechas_horas(
    fecha_inicio: date,
    fecha_fin: date,
    hora_inicio: time,
    hora_fin: time
) -> None:
    if fecha_fin < fecha_inicio:
        raise ValueError("fecha_fin no puede ser menor que fecha_inicio.")
    if fecha_inicio == fecha_fin and hora_fin <= hora_inicio:
        raise ValueError("En el mismo día, hora_fin debe ser mayor que hora_inicio.")

async def _validar_responsable_puede_crear(session: AsyncSession, id_responsable: int) -> UsuarioModel:
    stmt = select(UsuarioModel).where(UsuarioModel.id_usuario == id_responsable)
    res = await session.execute(stmt)
    usuario = res.scalar_one_or_none()
    if not usuario:
        raise ValueError(f"Usuario responsable con id {id_responsable} no existe.")
    if usuario.rol not in ("estudiante", "docente"):
        raise PermissionError("Solo usuarios con rol 'estudiante' o 'docente' pueden crear eventos.")
    return usuario

# -----------------------------
# Services (fachada de negocio)
# -----------------------------
async def crear_evento_service(
    session: AsyncSession,
    evento_in,              # Espera tu schema pydantic: EventoCrear
    id_responsable: int
) -> EventoModel:
    """
    Reglas de negocio:
      - Validar rol del responsable (estudiante/docente).
      - Validar coherencia fecha/hora.
      - Forzar estado inicial 'registrado' (lo hace el CRUD v2).
      - Crear evento y responsable en la misma transacción (lo hace el CRUD v2).
    """
    await _validar_responsable_puede_crear(session, id_responsable)
    _validar_fechas_horas(
        fecha_inicio=evento_in.fecha_inicio,
        fecha_fin=evento_in.fecha_fin,
        hora_inicio=evento_in.hora_inicio,
        hora_fin=evento_in.hora_fin
    )
    # Delegamos al CRUD v2 (que crea evento + responsable)
    evento = await crud_crear_evento(session, evento_in, id_responsable)
    return evento

async def listar_eventos_service(
    session: AsyncSession,
    estado: Optional[EstadoEventoEnum] = None,
    tipo: Optional[TipoEventoEnum] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
) -> Sequence[EventoModel]:
    """
    Si tu CRUD v2 no implementa filtros, puedes:
      - (A) extender el CRUD para aceptar filtros (recomendado), o
      - (B) traer todo y filtrar en memoria (no recomendado en producción).
    Aquí asumimos que el CRUD ya puede listar, con o sin filtros.
    """
    # Si tu CRUD.listar_eventos no acepta filtros aún, cambia esta llamada y filtra aquí.
    eventos = await crud_listar_eventos(session)  # <- reemplaza por la versión con filtros cuando la tengas
    # Filtro opcional simple en memoria (temporal, si tu CRUD no tiene filtros)
    if estado is not None:
        eventos = [e for e in eventos if e.estado == estado]
    if tipo is not None:
        eventos = [e for e in eventos if e.tipo == tipo]
    if desde is not None:
        eventos = [e for e in eventos if e.fecha_inicio >= desde]
    if hasta is not None:
        eventos = [e for e in eventos if e.fecha_inicio <= hasta]
    return eventos

async def obtener_evento_service(session: AsyncSession, id_evento: int) -> Optional[EventoModel]:
    return await crud_buscar_evento_por_id(session, id_evento)

async def actualizar_evento_service(
    session: AsyncSession,
    id_evento: int,
    datos_actualizados: Dict[str, Any]
) -> Optional[EventoModel]:
    """
    Reglas:
      - Solo si estado = 'registrado' (lo valida el CRUD y aquí revalidamos fechas si vienen).
    """
    # Validaciones de coherencia solo si los campos vienen en el payload
    fi = datos_actualizados.get("fecha_inicio")
    ff = datos_actualizados.get("fecha_fin")
    hi = datos_actualizados.get("hora_inicio")
    hf = datos_actualizados.get("hora_fin")
    # Si vienen pares suficientes, valida
    if fi is not None and ff is not None and hi is not None and hf is not None:
        _validar_fechas_horas(fi, ff, hi, hf)
    # Delegar al CRUD v2 (usa dict)
    evento = await crud_actualizar_evento(session, id_evento, datos_actualizados)
    return evento

async def eliminar_evento_service(session: AsyncSession, id_evento: int) -> bool:
    """
    Reglas:
      - Solo si estado = 'registrado' (lo valida el CRUD v2).
    """
    return await crud_eliminar_evento(session, id_evento)
