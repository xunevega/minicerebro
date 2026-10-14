"""Fichas de oficio editables: semilla del repositorio + ediciones guardadas en la base.

Los YAML de app/oficio/fichas son la semilla. Lo que se edita o crea desde la app
se guarda en oficio_fichas (con historial en oficio_ficha_versiones) y sustituye a
la ficha de la semilla. Ver docs/POLITICA_CONOCIMIENTO.md, «Fichas editables».
"""

from __future__ import annotations

from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import OficioFichaRecord, OficioFichaVersionRecord, OficioPropuestaRecord
from app.oficio.catalog import Ficha, load_fichas
from app.oficio.selection import check_ficha_signals


class FichaInvalida(ValueError):
    """La ficha no cumple el formato o sus señales no superan la comprobación."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


_cache_lock = Lock()
_cache_key: tuple | None = None
_cache_value: dict[str, Ficha] | None = None
_cache_inactive: set[str] = set()


def _catalog_key(session: Session) -> tuple:
    count, latest = session.execute(
        select(func.count(OficioFichaRecord.id), func.max(OficioFichaRecord.updated_at))
    ).one()
    return (count, latest)


def active_fichas(session: Session) -> dict[str, Ficha]:
    """Catálogo vigente: semilla + ediciones, sin las fichas desactivadas.

    Se recarga solo cuando cambia algo en la base (una consulta ligera por llamada).
    """
    global _cache_key, _cache_value, _cache_inactive
    key = _catalog_key(session)
    with _cache_lock:
        if _cache_value is not None and key == _cache_key:
            return _cache_value
    fichas = dict(load_fichas())
    inactive: set[str] = set()
    for record in session.scalars(select(OficioFichaRecord)).all():
        if not record.activa:
            fichas.pop(record.id, None)
            inactive.add(record.id)
            continue
        try:
            fichas[record.id] = Ficha.model_validate(record.data)
        except ValidationError:
            # Una ficha guardada que ya no valida (por un cambio de formato) no rompe el resto.
            continue
    with _cache_lock:
        _cache_key, _cache_value, _cache_inactive = key, fichas, inactive
    return fichas


def ficha_metadata(session: Session) -> dict[str, dict]:
    """Versión, origen y estado de cada ficha, para la Biblioteca."""
    seed = load_fichas()
    meta = {
        ficha_id: {"version": 0, "origen": "semilla", "activa": True, "updated_at": None}
        for ficha_id in seed
    }
    for record in session.scalars(select(OficioFichaRecord)).all():
        meta[record.id] = {
            "version": record.version,
            "origen": record.origen,
            "activa": record.activa,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }
    return meta


def all_fichas_for_editing(session: Session) -> dict[str, Ficha]:
    """Todas las fichas, también las desactivadas, para poder reactivarlas."""
    fichas = dict(load_fichas())
    for record in session.scalars(select(OficioFichaRecord)).all():
        try:
            fichas[record.id] = Ficha.model_validate(record.data)
        except ValidationError:
            continue
    return fichas


def validate_ficha(session: Session, data: dict, ficha_id: str | None = None) -> tuple[Ficha | None, list[str]]:
    """Valida una ficha contra el formato, las relaciones y la calidad de sus señales."""
    try:
        ficha = Ficha.model_validate(data)
    except ValidationError as exc:
        problems = []
        for error in exc.errors():
            where = ".".join(str(part) for part in error.get("loc", ()))
            problems.append(f"{where}: {error.get('msg')}" if where else str(error.get("msg")))
        return None, problems
    problems: list[str] = []
    if ficha_id is not None and ficha.id != ficha_id:
        problems.append("No se puede cambiar el identificador de una ficha existente.")
    catalog = active_fichas(session)
    for relacion in ficha.relaciones:
        if relacion.ficha not in catalog and relacion.ficha != ficha.id:
            problems.append(f"La relación apunta a una ficha que no existe o está desactivada: {relacion.ficha}.")
    others = [other for other in catalog.values() if other.id != ficha.id]
    problems.extend(check_ficha_signals(ficha, others))
    return ficha, problems


def save_ficha(
    session: Session,
    data: dict,
    *,
    motivo: str,
    autor: str,
    nueva: bool,
    activa: bool = True,
) -> Ficha:
    ficha_id = str(data.get("id", "")).strip()
    exists = ficha_id in all_fichas_for_editing(session)
    if nueva and exists:
        raise FichaInvalida([f"Ya existe una ficha con el identificador «{ficha_id}»."])
    if not nueva and not exists:
        raise KeyError(ficha_id)
    if not motivo.strip():
        raise FichaInvalida(["Indica el motivo del cambio."])
    ficha, problems = validate_ficha(session, data, None if nueva else ficha_id)
    if ficha is None or problems:
        raise FichaInvalida(problems)

    now = datetime.now(UTC)
    record = session.get(OficioFichaRecord, ficha.id)
    if record is None:
        record = OficioFichaRecord(
            id=ficha.id,
            data=ficha.model_dump(),
            version=1,
            origen="nueva" if nueva else "editada",
            activa=activa,
            updated_by=autor,
            updated_at=now,
        )
        session.add(record)
        if not nueva:
            # Guarda la semilla como versión 0 para poder volver a ella.
            seed = load_fichas().get(ficha.id)
            if seed is not None:
                session.add(_version_record(ficha.id, 0, seed.model_dump(), True, "Versión del repositorio", "semilla", now))
    else:
        record.data = ficha.model_dump()
        record.version += 1
        record.activa = activa
        record.updated_by = autor
        record.updated_at = now
    session.add(_version_record(ficha.id, record.version, ficha.model_dump(), activa, motivo.strip(), autor, now))
    session.flush()
    return ficha


def set_active(session: Session, ficha_id: str, activa: bool, *, motivo: str, autor: str) -> None:
    fichas = all_fichas_for_editing(session)
    if ficha_id not in fichas:
        raise KeyError(ficha_id)
    if not activa:
        dependants = [
            other.nombre
            for other in active_fichas(session).values()
            if any(relacion.ficha == ficha_id for relacion in other.relaciones)
        ]
        if dependants:
            raise FichaInvalida(
                ["Otras fichas se relacionan con esta: " + ", ".join(sorted(dependants)) + ". Quita antes esas relaciones."]
            )
    save_ficha(
        session,
        fichas[ficha_id].model_dump(),
        motivo=motivo or ("Ficha reactivada" if activa else "Ficha desactivada"),
        autor=autor,
        nueva=False,
        activa=activa,
    )


def versions(session: Session, ficha_id: str) -> list[dict]:
    records = session.scalars(
        select(OficioFichaVersionRecord)
        .where(OficioFichaVersionRecord.ficha_id == ficha_id)
        .order_by(OficioFichaVersionRecord.version.desc())
    ).all()
    return [
        {
            "version": record.version,
            "data": record.data,
            "activa": record.activa,
            "motivo": record.motivo,
            "autor": record.autor,
            "created_at": record.created_at.isoformat(),
        }
        for record in records
    ]


def restore_version(session: Session, ficha_id: str, version: int, *, autor: str) -> Ficha:
    record = session.scalar(
        select(OficioFichaVersionRecord).where(
            OficioFichaVersionRecord.ficha_id == ficha_id,
            OficioFichaVersionRecord.version == version,
        )
    )
    if record is None:
        raise KeyError(f"{ficha_id}@{version}")
    return save_ficha(
        session,
        record.data,
        motivo=f"Restaurada la versión {version}",
        autor=autor,
        nueva=False,
        activa=True,
    )


def _version_record(ficha_id, version, data, activa, motivo, autor, now) -> OficioFichaVersionRecord:
    return OficioFichaVersionRecord(
        id=str(uuid4()),
        ficha_id=ficha_id,
        version=version,
        data=data,
        activa=activa,
        motivo=motivo,
        autor=autor,
        created_at=now,
    )


# --- Propuestas de mejora ---


def proposal_out(record: OficioPropuestaRecord, current: Ficha | None) -> dict:
    return {
        "id": record.id,
        "ficha_id": record.ficha_id,
        "tipo": record.tipo,
        "motivo": record.motivo,
        "evidencia": record.evidencia,
        "estado": record.estado,
        "propuesta": record.data,
        "actual": current.model_dump() if current else None,
        "created_at": record.created_at.isoformat(),
        "decided_at": record.decided_at.isoformat() if record.decided_at else None,
    }


def list_proposals(session: Session, estado: str | None = "pendiente") -> list[dict]:
    query = select(OficioPropuestaRecord).order_by(OficioPropuestaRecord.created_at.desc())
    if estado:
        query = query.where(OficioPropuestaRecord.estado == estado)
    fichas = all_fichas_for_editing(session)
    return [proposal_out(record, fichas.get(record.ficha_id)) for record in session.scalars(query).all()]


def add_proposal(session: Session, ficha_id: str, tipo: str, data: dict, motivo: str, evidencia: dict) -> OficioPropuestaRecord:
    record = OficioPropuestaRecord(
        id=str(uuid4()),
        ficha_id=ficha_id,
        tipo=tipo,
        data=data,
        motivo=motivo,
        evidencia=evidencia,
        estado="pendiente",
        created_at=datetime.now(UTC),
        decided_by="",
    )
    session.add(record)
    session.flush()
    return record


def decide_proposal(session: Session, proposal_id: str, accept: bool, *, autor: str, data: dict | None = None) -> dict:
    record = session.get(OficioPropuestaRecord, proposal_id)
    if record is None:
        raise KeyError(proposal_id)
    if record.estado != "pendiente":
        raise FichaInvalida(["Esta propuesta ya está decidida."])
    if accept:
        payload = data or record.data
        save_ficha(
            session,
            payload,
            motivo=f"Propuesta aceptada: {record.motivo}",
            autor=autor,
            nueva=record.tipo == "crear",
        )
    record.estado = "aceptada" if accept else "rechazada"
    record.decided_at = datetime.now(UTC)
    record.decided_by = autor
    session.flush()
    return proposal_out(record, all_fichas_for_editing(session).get(record.ficha_id))
