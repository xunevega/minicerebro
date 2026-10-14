"""Fichas de oficio: conocimiento que Editados envía al modelo.

Ver docs/POLITICA_CONOCIMIENTO.md.
"""

from app.oficio.catalog import Ficha, load_fichas
from app.oficio.selection import SelectedFicha, oficio_block, select_fichas

__all__ = ["Ficha", "SelectedFicha", "load_fichas", "oficio_block", "select_fichas"]
