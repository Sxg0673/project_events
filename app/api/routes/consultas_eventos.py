# app/api/routes/consultas_eventos.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import List, Dict, Any

from app.db.mysql import get_session
from app.crud.eventos import consultas as q

# (Opcional) usar schema para serializar eventos en la #3
from app.schemas.eventos.evento import Evento as EventoOut

router = APIRouter(prefix="/consultas", tags=["Consultas analíticas"])


@router.get("/organizaciones/{id_organizacion}/resumen")
async def consulta_1_resumen_por_organizacion(
    id_organizacion: int,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    return await q.q1_eventos_por_organizacion(session, id_organizacion)


@router.get("/instalaciones/{id_instalacion}/resumen")
async def consulta_2_resumen_por_instalacion(
    id_instalacion: int,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    return await q.q2_resumen_por_instalacion(session, id_instalacion)


@router.get("/eventos/pendientes", response_model=List[EventoOut])
async def consulta_3_eventos_pendientes_por_periodo(
    desde: date = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    hasta: date = Query(..., description="Fecha final (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session),
):
    if hasta < desde:
        raise HTTPException(status_code=400, detail="El parámetro 'hasta' no puede ser menor que 'desde'.")
    eventos = await q.q3_pendientes_por_periodo(session, desde, hasta)
    # Serializamos con el schema Pydantic
    return [EventoOut.model_validate(e, from_attributes=True) for e in eventos]


@router.get("/instalaciones/top")
async def consulta_4_instalacion_top_y_detalle(
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    return await q.q4_instalacion_top_y_detalle(session)


@router.get("/organizadores/unidades/resumen")
async def consulta_5_eventos_por_unidad_organizadora(
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    return await q.q5_eventos_por_unidad_organizadora(session)


@router.get("/credenciales/activas-vencidas")
async def consulta_6_usuarios_con_password_activa_vencida(
    fecha_base: date | None = Query(None, description="Fecha de referencia (opcional). Si no se envía, hoy()."),
    session: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    return await q.q6_usuarios_con_password_activa_vencida(session, fecha_base)


@router.get("/representantes/proporcion-por-rol")
async def consulta_7_proporcion_representantes_por_rol(
    session: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    return await q.q7_proporcion_representantes_por_rol_organizador(session)


@router.get("/usuarios/resumen-participacion")
async def consulta_8_usuarios_por_rol_y_mas_participa(
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    return await q.q8_usuarios_por_rol_y_mas_participa(session)


@router.get("/organizadores/top")
async def consulta_9_top5_usuarios_activos(
    desde: date = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    hasta: date = Query(..., description="Fecha final (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    if hasta < desde:
        raise HTTPException(status_code=400, detail="El parámetro 'hasta' no puede ser menor que 'desde'.")
    return await q.q9_top5_usuarios_activos(session, desde, hasta)


@router.get("/eventos/revisiones/tasa-rechazo")
async def consulta_10_tasa_rechazo_y_revisiones(
    session: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    return await q.q10_rechazo_inicial_y_revisiones(session)