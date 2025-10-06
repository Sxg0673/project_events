from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.mysql import get_session
from app.services.eventos import representante_service as svc
from app.schemas.eventos.representante import Representante, RepresentanteCrear

router = APIRouter(prefix="/eventos", tags=["Participación externa"])


@router.post("/{id_evento}/organizaciones", response_model=Representante, status_code=status.HTTP_201_CREATED)
async def agregar_organizacion_a_evento(
    id_evento: int,
    # Campos simples (Form para combinar con archivo)
    id_organizacion: int = Form(..., description="ID de la organización externa"),
    nombre_representante: str = Form(..., description="Nombre de quien asistirá"),
    representante_legal: str = Form(..., description="'Si' o 'No'"),
    certificado: Optional[UploadFile] = File(None, description="PDF firmado por el representante legal"),
    session: AsyncSession = Depends(get_session),
):
    try:
        certificado_bytes = await certificado.read() if certificado else None
        rep = await svc.agregar_representante_service(
            session, id_evento, id_organizacion, nombre_representante, representante_legal, certificado_bytes
        )
        return rep
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id_evento}/organizaciones", response_model=List[Representante], status_code=status.HTTP_200_OK)
async def listar_organizaciones_de_evento(
    id_evento: int,
    session: AsyncSession = Depends(get_session),
):
    reps = await svc.listar_representantes_por_evento_service(session, id_evento)
    return reps


@router.delete("/{id_evento}/organizaciones/{id_organizacion}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_organizacion_de_evento(
    id_evento: int,
    id_organizacion: int,
    session: AsyncSession = Depends(get_session),
):
    try:
        ok = await svc.eliminar_representante_service(session, id_evento, id_organizacion)
        if not ok:
            raise HTTPException(status_code=404, detail="Vínculo evento-organización no encontrado")
        return
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id_evento}/organizaciones/{id_organizacion}/certificado", responses={
    200: {"content": {"application/pdf": {}}}
})
async def descargar_certificado(
    id_evento: int,
    id_organizacion: int,
    session: AsyncSession = Depends(get_session),
):
    cert = await svc.obtener_certificado_service(session, id_evento, id_organizacion)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certificado no encontrado")
    return Response(content=cert, media_type="application/pdf")
