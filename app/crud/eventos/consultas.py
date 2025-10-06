# app/crud/eventos/consultas.py
from typing import Optional, Sequence, Dict, Any, List, Tuple
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, desc, text
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import over

from app.models.eventos.evento import EventoModel, TipoEventoEnum, EstadoEventoEnum
from app.models.eventos.representante import RepresentanteModel
from app.models.eventos.evento_responsable import EventoResponsableModel
from app.models.eventos.instalacion_evento import InstalacionEventoModel
from app.models.usuarios.usuario import UsuarioModel
from app.models.usuarios.credencial import CredencialModel



# 1) Por organización externa: total de eventos y si participa más en lúdicos o académicos.
async def q1_eventos_por_organizacion(session: AsyncSession, id_organizacion: int) -> Dict[str, Any]:
    stmt = (
        select(EventoModel.tipo, func.count().label("n"))
        .join(RepresentanteModel, RepresentanteModel.id_evento == EventoModel.id_evento)
        .where(RepresentanteModel.id_organizacion == id_organizacion)
        .group_by(EventoModel.tipo)
    )
    res = (await session.execute(stmt)).all()
    por_tipo = {t.value if isinstance(t, TipoEventoEnum) else t: n for (t, n) in res}
    total = sum(por_tipo.values()) if por_tipo else 0
    predominante = None
    if por_tipo:
        predominante = max(por_tipo.items(), key=lambda x: x[1])[0]
    return {"id_organizacion": id_organizacion, "total": total, "por_tipo": por_tipo, "predominante": predominante}


# 2) Para una instalación: n° de eventos, tipo más frecuente, y organizadores por tipo
async def q2_resumen_por_instalacion(session: AsyncSession, id_instalacion: int) -> Dict[str, Any]:
    # total de eventos en la instalación
    total_stmt = (
        select(func.count().label("total"))
        .select_from(InstalacionEventoModel)
        .where(InstalacionEventoModel.id_instalacion == id_instalacion)
    )
    total = (await session.execute(total_stmt)).scalar_one()

    # frecuencia por tipo
    tipo_stmt = (
        select(EventoModel.tipo, func.count().label("n"))
        .join(InstalacionEventoModel, InstalacionEventoModel.id_evento == EventoModel.id_evento)
        .where(InstalacionEventoModel.id_instalacion == id_instalacion)
        .group_by(EventoModel.tipo)
    )
    tipo_rows = (await session.execute(tipo_stmt)).all()
    freq_por_tipo = {t.value if isinstance(t, TipoEventoEnum) else t: n for (t, n) in tipo_rows}
    tipo_mas_frecuente = max(freq_por_tipo, key=freq_por_tipo.get) if freq_por_tipo else None

    # organizadores según tipo
    org_stmt = (
        select(EventoModel.tipo, func.count(func.distinct(EventoResponsableModel.id_usuario)).label("organizadores"))
        .join(InstalacionEventoModel, InstalacionEventoModel.id_evento == EventoModel.id_evento)
        .join(EventoResponsableModel, EventoResponsableModel.id_evento == EventoModel.id_evento)
        .where(InstalacionEventoModel.id_instalacion == id_instalacion)
        .group_by(EventoModel.tipo)
    )
    org_rows = (await session.execute(org_stmt)).all()
    organizadores_por_tipo = {t.value if isinstance(t, TipoEventoEnum) else t: n for (t, n) in org_rows}

    return {
        "id_instalacion": id_instalacion,
        "total_eventos": total,
        "tipo_mas_frecuente": tipo_mas_frecuente,
        "organizadores_por_tipo": organizadores_por_tipo,
    }


# 3) Eventos "pendientes" por periodo, ordenados (asumo pendiente = EN_REVISION)
async def q3_pendientes_por_periodo(
    session: AsyncSession,
    desde: date,
    hasta: date,
    estado_pendiente: EstadoEventoEnum = EstadoEventoEnum.EN_REVISION,
) -> Sequence[EventoModel]:
    stmt = (
        select(EventoModel)
        .where(
            EventoModel.estado == estado_pendiente,
            EventoModel.fecha_inicio >= desde,
            EventoModel.fecha_inicio <= hasta,
        )
        .order_by(EventoModel.fecha_inicio.asc())
        .options(
            selectinload(EventoModel.responsables),
            selectinload(EventoModel.instalaciones),
            selectinload(EventoModel.organizaciones),
        )
    )
    return (await session.execute(stmt)).scalars().all()


# 4) Instalación más asignada + frecuencias de tipo allí + total organizadores
async def q4_instalacion_top_y_detalle(session: AsyncSession) -> Dict[str, Any]:
    # instalación con más asignaciones
    top_stmt = (
        select(InstalacionEventoModel.id_instalacion, func.count().label("n"))
        .group_by(InstalacionEventoModel.id_instalacion)
        .order_by(desc("n"))
        .limit(1)
    )
    top_row = (await session.execute(top_stmt)).first()
    if not top_row:
        return {"id_instalacion": None, "total_eventos": 0, "frecuencia_por_tipo": {}, "organizadores_totales": 0}
    id_instalacion, total_eventos = top_row

    # frecuencias por tipo
    freq_stmt = (
        select(EventoModel.tipo, func.count().label("n"))
        .join(InstalacionEventoModel, InstalacionEventoModel.id_evento == EventoModel.id_evento)
        .where(InstalacionEventoModel.id_instalacion == id_instalacion)
        .group_by(EventoModel.tipo)
    )
    freq_rows = (await session.execute(freq_stmt)).all()
    frecuencia_por_tipo = {t.value if isinstance(t, TipoEventoEnum) else t: n for (t, n) in freq_rows}

    # organizadores totales (distintos) que han hecho parte de un evento en esa instalación
    org_stmt = (
        select(func.count(func.distinct(EventoResponsableModel.id_usuario)))
        .join(EventoModel, EventoModel.id_evento == EventoResponsableModel.id_evento)
        .join(InstalacionEventoModel, InstalacionEventoModel.id_evento == EventoModel.id_evento)
        .where(InstalacionEventoModel.id_instalacion == id_instalacion)
    )
    organizadores_totales = (await session.execute(org_stmt)).scalar_one()

    return {
        "id_instalacion": id_instalacion,
        "total_eventos": total_eventos,
        "frecuencia_por_tipo": frecuencia_por_tipo,
        "organizadores_totales": organizadores_totales,
    }


# 5) N° total de eventos por "unidad organizadora" + total de organizadores + total de entidades externas
#    Interpretación: 
#    - Para DOCENTES: agrupar por Unidad Académica
#    - Para ESTUDIANTES: agrupar por Programa
#    (si quieres, luego unificas en la capa de servicio)
async def q5_eventos_por_unidad_organizadora(session: AsyncSession) -> Dict[str, List[Dict[str, Any]]]:
    # docentes por unidad_academica
    from app.models.usuarios.docente import DocenteModel
    from app.models.organizaciones.unidad_academica import UnidadAcademicaModel
    doc_stmt = (
        select(
            UnidadAcademicaModel.id_unidad_academica.label("id_unidad"),
            func.count(func.distinct(EventoModel.id_evento)).label("eventos"),
            func.count(func.distinct(EventoResponsableModel.id_usuario)).label("organizadores"),
            func.count(func.distinct(RepresentanteModel.id_organizacion)).label("entidades_externas"),
        )
        .join(EventoResponsableModel, EventoResponsableModel.id_evento == EventoModel.id_evento)
        .join(DocenteModel, DocenteModel.id_usuario == EventoResponsableModel.id_usuario)
        .join(UnidadAcademicaModel, UnidadAcademicaModel.id_unidad_academica == DocenteModel.id_unidad_academica)
        .outerjoin(RepresentanteModel, RepresentanteModel.id_evento == EventoModel.id_evento)
        .group_by(UnidadAcademicaModel.id_unidad_academica)
    )
    docentes = [dict(r._mapping) for r in (await session.execute(doc_stmt)).all()]

    # estudiantes por programa
    from app.models.usuarios.estudiante import EstudianteModel
    from app.models.organizaciones.programa import ProgramaModel
    est_stmt = (
        select(
            ProgramaModel.id_programa.label("id_unidad"),
            func.count(func.distinct(EventoModel.id_evento)).label("eventos"),
            func.count(func.distinct(EventoResponsableModel.id_usuario)).label("organizadores"),
            func.count(func.distinct(RepresentanteModel.id_organizacion)).label("entidades_externas"),
        )
        .join(EventoResponsableModel, EventoResponsableModel.id_evento == EventoModel.id_evento)
        .join(EstudianteModel, EstudianteModel.id_usuario == EventoResponsableModel.id_usuario)
        .join(ProgramaModel, ProgramaModel.id_programa == EstudianteModel.id_programa)
        .outerjoin(RepresentanteModel, RepresentanteModel.id_evento == EventoModel.id_evento)
        .group_by(ProgramaModel.id_programa)
    )
    estudiantes = [dict(r._mapping) for r in (await session.execute(est_stmt)).all()]

    return {"por_unidad_academica_docentes": docentes, "por_programa_estudiantes": estudiantes}


# 6) Usuarios con contraseña ACTIVA sin renovar hace > 6 meses (devolver usuario + rol)
async def q6_usuarios_con_password_activa_vencida(session: AsyncSession, hoy: Optional[date] = None) -> List[Dict[str, Any]]:
    hoy = hoy or date.today()
    # cutoff 6 meses atrás
    # Computamos cutoff en Python para no depender de funciones MySQL específicas
    six_months_ago = hoy - timedelta(days=6 * 30)  # aproximación 180 días

    c = CredencialModel
    u = UsuarioModel
    stmt = (
        select(u.id_usuario, u.rol, c.fecha_creacion.label("fecha_cambio"))
        .join(c, c.id_usuario == u.id_usuario)
        .where(
            c.estado == "activa",
            c.fecha_creacion <= six_months_ago,
        )
    )
    rows = (await session.execute(stmt)).all()
    return [dict(id_usuario=i, rol=r, fecha_cambio=f) for (i, r, f) in rows]


# 7) Proporción de representantes legales vs no legales por tipo de organizador (docente/estudiante)
async def q7_proporcion_representantes_por_rol_organizador(session: AsyncSession) -> List[Dict[str, Any]]:
    # Asumimos 1 responsable por evento (tu decisión de diseño)
    # rol organizador lo tomamos del Usuario del EventoResponsable
    stmt = (
        select(
            UsuarioModel.rol,
            func.sum(case((RepresentanteModel.representante_legal == "Si", 1), else_=0)).label("legales"),
            func.sum(case((RepresentanteModel.representante_legal == "No", 1), else_=0)).label("no_legales"),
            func.count().label("total")
        )
        .join(EventoResponsableModel, EventoResponsableModel.id_usuario == UsuarioModel.id_usuario)
        .join(RepresentanteModel, RepresentanteModel.id_evento == EventoResponsableModel.id_evento)
        .group_by(UsuarioModel.rol)
    )
    rows = (await session.execute(stmt)).all()
    out = []
    for rol, legales, no_legales, total in rows:
        p_leg = (legales / total) * 100 if total else 0
        p_noleg = (no_legales / total) * 100 if total else 0
        out.append({"rol": rol, "legales": legales, "no_legales": no_legales, "p_legales": p_leg, "p_no_legales": p_noleg})
    return out


# 8) Conteo de usuarios por rol y comparación con el rol que más participa organizando eventos
async def q8_usuarios_por_rol_y_mas_participa(session: AsyncSession) -> Dict[str, Any]:
    # usuarios por rol
    u_stmt = select(UsuarioModel.rol, func.count().label("n")).group_by(UsuarioModel.rol)
    usuarios_por_rol = {rol: n for (rol, n) in (await session.execute(u_stmt)).all()}

    # participación por rol (usuarios que han organizado al menos un evento)
    part_stmt = (
        select(UsuarioModel.rol, func.count(func.distinct(UsuarioModel.id_usuario)).label("n"))
        .join(EventoResponsableModel, EventoResponsableModel.id_usuario == UsuarioModel.id_usuario)
        .group_by(UsuarioModel.rol)
    )
    participa_por_rol = {rol: n for (rol, n) in (await session.execute(part_stmt)).all()}

    tipo_mas_registrado = max(usuarios_por_rol, key=usuarios_por_rol.get) if usuarios_por_rol else None
    tipo_que_mas_participa = max(participa_por_rol, key=participa_por_rol.get) if participa_por_rol else None

    return {
        "usuarios_por_rol": usuarios_por_rol,
        "participa_por_rol": participa_por_rol,
        "tipo_mas_registrado": tipo_mas_registrado,
        "tipo_que_mas_participa": tipo_que_mas_participa,
    }


# 9) Top 5 usuarios más activos en un periodo, con instalación más usada y % por tipo
async def q9_top5_usuarios_activos(
    session: AsyncSession,
    desde: date,
    hasta: date
) -> List[Dict[str, Any]]:
    # total de eventos por usuario en el periodo
    base_evt = (
        select(
            EventoResponsableModel.id_usuario.label("id_usuario"),
            func.count(func.distinct(EventoModel.id_evento)).label("n_eventos")
        )
        .join(EventoModel, EventoModel.id_evento == EventoResponsableModel.id_evento)
        .where(EventoModel.fecha_inicio >= desde, EventoModel.fecha_inicio <= hasta)
        .group_by(EventoResponsableModel.id_usuario)
        .order_by(desc("n_eventos"))
        .limit(5)
    )
    top = (await session.execute(base_evt)).all()
    top_ids = [r.id_usuario for r in top]
    if not top_ids:
        return []

    # instalación más usada por cada usuario
    inst_stmt = (
        select(
            EventoResponsableModel.id_usuario.label("id_usuario"),
            InstalacionEventoModel.id_instalacion,
            func.count().label("n")
        )
        .join(InstalacionEventoModel, InstalacionEventoModel.id_evento == EventoResponsableModel.id_evento)
        .join(EventoModel, EventoModel.id_evento == EventoResponsableModel.id_evento)
        .where(
            EventoResponsableModel.id_usuario.in_(top_ids),
            EventoModel.fecha_inicio >= desde, EventoModel.fecha_inicio <= hasta
        )
        .group_by(EventoResponsableModel.id_usuario, InstalacionEventoModel.id_instalacion)
        .order_by(EventoResponsableModel.id_usuario, desc("n"))
    )
    inst_rows = (await session.execute(inst_stmt)).all()
    # elegir la de mayor n por usuario
    top_inst_por_usuario = {}
    for uid, id_inst, n in inst_rows:
        if uid not in top_inst_por_usuario:
            top_inst_por_usuario[uid] = {"id_instalacion": id_inst, "uso": n}

    # % por tipo para cada usuario
    tipo_stmt = (
        select(
            EventoResponsableModel.id_usuario,
            EventoModel.tipo,
            func.count().label("n")
        )
        .join(EventoModel, EventoModel.id_evento == EventoResponsableModel.id_evento)
        .where(
            EventoResponsableModel.id_usuario.in_(top_ids),
            EventoModel.fecha_inicio >= desde, EventoModel.fecha_inicio <= hasta
        )
        .group_by(EventoResponsableModel.id_usuario, EventoModel.tipo)
    )
    tipo_rows = (await session.execute(tipo_stmt)).all()
    conteos_tipo = {}
    for uid, t, n in tipo_rows:
        tval = t.value if isinstance(t, TipoEventoEnum) else t
        conteos_tipo.setdefault(uid, {"total": 0, "por_tipo": {}})
        conteos_tipo[uid]["por_tipo"][tval] = n
        conteos_tipo[uid]["total"] += n

    # ensamblar salida
    salida = []
    for r in top:
        uid, n_evts = r
        por_tipo = conteos_tipo.get(uid, {"total": 0, "por_tipo": {}})
        total = por_tipo["total"]
        pct = {
            k: (v * 100 / total) if total else 0
            for k, v in por_tipo["por_tipo"].items()
        }
        salida.append({
            "id_usuario": uid,
            "eventos": n_evts,
            "instalacion_mas_usada": top_inst_por_usuario.get(uid, {}).get("id_instalacion"),
            "porcentaje_por_tipo": pct
        })
    return salida


# 10) Tasa de rechazo inicial y promedio de revisiones hasta aprobación final (por tipo de evento)
async def q10_rechazo_inicial_y_revisiones(session: AsyncSession) -> List[Dict[str, Any]]:
    from app.models.eventos.evaluacion import EvaluacionModel

    # Row number por evento por fecha_evaluacion
    # MySQL 8+ soporta window functions
    rn = func.row_number().over(
        partition_by=EvaluacionModel.id_evento,
        order_by=EvaluacionModel.fecha_evaluacion.asc()
    )

    # primera evaluación de cada evento + tipo
    first_eval_stmt = (
        select(
            EventoModel.tipo.label("tipo"),
            EvaluacionModel.estado.label("estado")
        )
        .join(EvaluacionModel, EvaluacionModel.id_evento == EventoModel.id_evento)
        .where(rn == 1)  # filtrado por window en subconsulta
    )

    # SQLAlchemy requiere subconsulta para filtrar por funciones ventana
    sub_first = (
        select(
            EventoModel.tipo.label("tipo"),
            EvaluacionModel.estado.label("estado"),
            rn.label("rn")
        )
        .join(EvaluacionModel, EvaluacionModel.id_evento == EventoModel.id_evento)
        .subquery()
    )
    first_agg = (
        select(
            sub_first.c.tipo,
            func.sum(case((sub_first.c.estado == "rechazado", 1), else_=0)).label("rechazos_iniciales"),
            func.count().label("con_evaluacion"),
        )
        .where(sub_first.c.rn == 1)
        .group_by(sub_first.c.tipo)
    )

    first_rows = (await session.execute(first_agg)).all()
    rechazo_inicial = {}
    for tipo, rej_ini, con_eval in first_rows:
        tval = tipo.value if isinstance(tipo, TipoEventoEnum) else tipo
        tasa = (rej_ini / con_eval) * 100 if con_eval else 0
        rechazo_inicial[tval] = {"rechazos_iniciales": rej_ini, "con_evaluacion": con_eval, "tasa_pct": tasa}

    # revisiones hasta la aprobación: posición de la primera 'aprobado'
    rn_aprob = func.row_number().over(
        partition_by=EvaluacionModel.id_evento,
        order_by=EvaluacionModel.fecha_evaluacion.asc()
    )
    sub_rev = (
        select(
            EventoModel.tipo.label("tipo"),
            EvaluacionModel.id_evento,
            rn_aprob.label("posicion"),
            EvaluacionModel.estado
        )
        .join(EvaluacionModel, EvaluacionModel.id_evento == EventoModel.id_evento)
        .subquery()
    )
    # nos quedamos con la mínima posicion donde estado='aprobado'
    aprob_min = (
        select(
            sub_rev.c.tipo,
            func.avg(sub_rev.c.posicion).label("prom_revisiones_hasta_aprob")
        )
        .where(sub_rev.c.estado == "aprobado")
        .group_by(sub_rev.c.tipo)
    )
    aprob_rows = (await session.execute(aprob_min)).all()
    revisiones = { (t.value if isinstance(t, TipoEventoEnum) else t): float(p or 0) for (t, p) in aprob_rows }

    # merge final por tipo
    tipos = set(list(rechazo_inicial.keys()) + list(revisiones.keys()))
    salida = []
    for t in tipos:
        salida.append({
            "tipo": t,
            "rechazo_inicial": rechazo_inicial.get(t, {}),
            "prom_revisiones_hasta_aprob": revisiones.get(t, 0.0)
        })
    return salida