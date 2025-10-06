from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.eventos import representante as crud_rep
from app.models.eventos.representante import RepresentanteModel


async def agregar_representante_service(
    session: AsyncSession,
    id_evento: int,
    id_organizacion: int,
    nombre_representante: str,
    representante_legal: str,           # 'Si' | 'No'
    certificado_bytes: Optional[bytes],
) -> RepresentanteModel:
    # Aquí podrías validar 'Si'/'No' explícitamente si quieres
    if representante_legal not in ("Si", "No"):
        raise ValueError("representante_legal debe ser 'Si' o 'No'")
    return await crud_rep.agregar_representante(
        session, id_evento, id_organizacion, nombre_representante, representante_legal, certificado_bytes
    )


async def listar_representantes_por_evento_service(
    session: AsyncSession, id_evento: int
) -> List[RepresentanteModel]:
    return await crud_rep.listar_representantes_por_evento(session, id_evento)


async def eliminar_representante_service(
    session: AsyncSession, id_evento: int, id_organizacion: int
) -> bool:
    return await crud_rep.eliminar_representante(session, id_evento, id_organizacion)


async def obtener_certificado_service(
    session: AsyncSession, id_evento: int, id_organizacion: int
) -> Optional[bytes]:
    return await crud_rep.obtener_certificado(session, id_evento, id_organizacion)
