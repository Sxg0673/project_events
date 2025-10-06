from typing import List, Dict, Any, Optional
from datetime import date

from fastapi import APIRouter, Depends, status, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.mysql import get_session
from app.services.eventos import evento as evento_service
from app.schemas.eventos.evento import EventoCrear, Evento
from app.models.eventos.evento import EstadoEventoEnum, TipoEventoEnum

router = APIRouter(prefix="/eventos", tags=["Eventos"])

# POST /eventos  -> crear (requiere id_responsable estudiante/docente)
@router.post("/", response_model=Evento, status_code=status.HTTP_201_CREATED)
async def crear_evento(
    payload: EventoCrear,
    id_responsable: int = Query(..., description="ID del usuario (estudiante/docente) responsable"),
    session: AsyncSession = Depends(get_session),
):
    try:
        evt = await evento_service.crear_evento_service(session, payload, id_responsable)
        return evt
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# GET /eventos -> listar (filtros opcionales)
@router.get("/", response_model=List[Evento], status_code=status.HTTP_200_OK)
async def listar_eventos(
    estado: Optional[EstadoEventoEnum] = Query(None, description="registrado | en_revision | aprobado"),
    tipo: Optional[TipoEventoEnum] = Query(None, description="ludico | academico"),
    desde: Optional[date] = Query(None, description="YYYY-MM-DD"),
    hasta: Optional[date] = Query(None, description="YYYY-MM-DD"),
    session: AsyncSession = Depends(get_session),
):
    if desde and hasta and hasta < desde:
        raise HTTPException(status_code=400, detail="'hasta' no puede ser menor que 'desde'")
    eventos = await evento_service.listar_eventos_service(session, estado, tipo, desde, hasta)
    return eventos


# GET /eventos/{id} -> detalle
@router.get("/{id_evento}", response_model=Evento, status_code=status.HTTP_200_OK)
async def obtener_evento(
    id_evento: int,
    session: AsyncSession = Depends(get_session),
):
    evt = await evento_service.obtener_evento_service(session, id_evento)
    if not evt:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return evt


# PATCH /eventos/{id} -> actualizar (solo si estado = registrado)
@router.patch("/{id_evento}", response_model=Evento, status_code=status.HTTP_200_OK)
async def actualizar_evento(
    id_evento: int,
    datos: Dict[str, Any] = Body(..., description="Campos a actualizar"),
    session: AsyncSession = Depends(get_session),
):
    try:
        evt = await evento_service.actualizar_evento_service(session, id_evento, datos)
        if not evt:
            # no existe o no está en estado permitido (el CRUD devuelve None en esos casos)
            raise HTTPException(status_code=409, detail="No se puede actualizar: evento inexistente o no está 'registrado'")
        return evt
    except ValueError as e:
        # incoherencias de fecha/hora u otras validaciones
        raise HTTPException(status_code=400, detail=str(e))


# DELETE /eventos/{id} -> eliminar (solo si estado = registrado)
@router.delete("/{id_evento}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_evento(
    id_evento: int,
    session: AsyncSession = Depends(get_session),
):
    try:
        ok = await evento_service.eliminar_evento_service(session, id_evento)
        if not ok:
            # no existe o no está en estado permitido
            raise HTTPException(status_code=409, detail="No se puede eliminar: evento inexistente o no está 'registrado'")
        return
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
