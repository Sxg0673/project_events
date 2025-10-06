from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.eventos.evento import EventoModel, EstadoEventoEnum
from app.models.organizaciones.organizacion import OrganizacionModel
from app.models.eventos.representante import RepresentanteModel


async def _verificar_evento_registrado(session: AsyncSession, id_evento: int) -> EventoModel:
    result = await session.execute(
        select(EventoModel).where(EventoModel.id_evento == id_evento)
    )
    evento = result.scalar_one_or_none()
    if not evento:
        raise ValueError("Evento no encontrado")
    if evento.estado != EstadoEventoEnum.REGISTRADO:
        raise ValueError("Solo se puede modificar participación externa si el evento está 'registrado'")
    return evento


async def _verificar_organizacion(session: AsyncSession, id_organizacion: int) -> OrganizacionModel:
    result = await session.execute(
        select(OrganizacionModel).where(OrganizacionModel.id_organizacion == id_organizacion)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise ValueError("Organización externa no encontrada")
    return org


async def agregar_representante(
    session: AsyncSession,
    id_evento: int,
    id_organizacion: int,
    nombre_representante: str,
    representante_legal: str,             # 'Si' | 'No'
    certificado_bytes: Optional[bytes],   # puede ser None
) -> RepresentanteModel:
    await _verificar_evento_registrado(session, id_evento)
    await _verificar_organizacion(session, id_organizacion)

    # ¿ya existe el vínculo?
    ya_q = await session.execute(
        select(RepresentanteModel).where(
            RepresentanteModel.id_evento == id_evento,
            RepresentanteModel.id_organizacion == id_organizacion
        )
    )
    ya = ya_q.scalar_one_or_none()
    if ya:
        raise ValueError("La organización ya está asociada a este evento")

    rep = RepresentanteModel(
        id_evento=id_evento,
        id_organizacion=id_organizacion,
        nombre_representante=nombre_representante,
        representante_legal=representante_legal,
        certificado_participacion=certificado_bytes
    )
    session.add(rep)
    await session.commit()
    await session.refresh(rep)
    return rep


async def listar_representantes_por_evento(
    session: AsyncSession, id_evento: int
) -> List[RepresentanteModel]:
    # No exige estado 'registrado' para consultar
    result = await session.execute(
        select(RepresentanteModel).where(RepresentanteModel.id_evento == id_evento)
    )
    return result.scalars().all()


async def eliminar_representante(
    session: AsyncSession, id_evento: int, id_organizacion: int
) -> bool:
    await _verificar_evento_registrado(session, id_evento)

    result = await session.execute(
        select(RepresentanteModel).where(
            RepresentanteModel.id_evento == id_evento,
            RepresentanteModel.id_organizacion == id_organizacion
        )
    )
    rep = result.scalar_one_or_none()
    if not rep:
        return False

    await session.delete(rep)
    await session.commit()
    return True


async def obtener_certificado(
    session: AsyncSession, id_evento: int, id_organizacion: int
) -> Optional[bytes]:
    result = await session.execute(
        select(RepresentanteModel).where(
            RepresentanteModel.id_evento == id_evento,
            RepresentanteModel.id_organizacion == id_organizacion
        )
    )
    rep = result.scalar_one_or_none()
    if not rep:
        return None
    return rep.certificado_participacion
