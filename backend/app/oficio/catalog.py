"""Carga y validación de las fichas de oficio (app/oficio/fichas/*.yaml)."""

import re
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

FICHAS_DIR = Path(__file__).parent / "fichas"
RAMAS = ("lengua", "recursos", "composicion", "voz", "generos", "criterio")
ACCIONES = ("correction", "rewrite", "sendable", "continue", "variants", "review", "read")
MIRADAS = ("comprension", "estructura", "tono", "limpieza")
METRICAS = (
    "frase_larga",
    "repeticion_cercana",
    "anafora",
    "deriva_estilo",
    "parrafo_largo",
    "bloque_unico",
)


class Ejemplo(BaseModel):
    mal: str = Field(min_length=1)
    bien: str = Field(min_length=1)
    porque: str = Field(min_length=1)


class Fuente(BaseModel):
    obra: str = Field(min_length=1)
    localizador: str = Field(min_length=1)


class Senal(BaseModel):
    patron: str
    sensible_mayusculas: bool = False
    # Buscar también en el texto sin tildes. Se desactiva cuando la tilde es lo que se busca.
    tambien_sin_tildes: bool = True

    @field_validator("patron")
    @classmethod
    def _compila(cls, value: str) -> str:
        re.compile(value)
        return value

    def regex(self) -> re.Pattern[str]:
        flags = re.UNICODE if self.sensible_mayusculas else re.IGNORECASE | re.UNICODE
        return re.compile(self.patron, flags)


class Base(BaseModel):
    acciones: list[Literal[ACCIONES]] = Field(default_factory=list)  # type: ignore[valid-type]
    miradas: list[Literal[MIRADAS]] = Field(default_factory=list)  # type: ignore[valid-type]


class Relacion(BaseModel):
    tipo: Literal["prioridad_sobre", "conflicto_con", "requiere"]
    ficha: str
    criterio: str = ""


class Ficha(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    rama: Literal[RAMAS]  # type: ignore[valid-type]
    nombre: str = Field(min_length=1)
    regla: str = Field(min_length=20)
    aplica: str = Field(min_length=1)
    no_aplica: str = Field(min_length=1)
    ejemplos: list[Ejemplo] = Field(min_length=1)
    fuente: Fuente
    senales: list[Senal] = Field(default_factory=list)
    metricas: list[Literal[METRICAS]] = Field(default_factory=list)  # type: ignore[valid-type]
    base: Base = Field(default_factory=Base)
    generos: list[str] = Field(default_factory=list)
    relaciones: list[Relacion] = Field(default_factory=list)

    @model_validator(mode="after")
    def _relacion_consigo_misma(self) -> "Ficha":
        if any(relacion.ficha == self.id for relacion in self.relaciones):
            raise ValueError(f"La ficha {self.id} se relaciona consigo misma")
        return self


@lru_cache(maxsize=1)
def load_fichas() -> dict[str, Ficha]:
    fichas: dict[str, Ficha] = {}
    for path in sorted(FICHAS_DIR.glob("*.yaml")):
        for raw in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            ficha = Ficha.model_validate(raw)
            if ficha.id in fichas:
                raise ValueError(f"Ficha duplicada: {ficha.id} ({path.name})")
            fichas[ficha.id] = ficha
    for ficha in fichas.values():
        for relacion in ficha.relaciones:
            if relacion.ficha not in fichas:
                raise ValueError(f"{ficha.id} se relaciona con una ficha inexistente: {relacion.ficha}")
    return fichas
