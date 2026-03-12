"""
Representación de los términos a evaluar (citas/citations).

Corresponde a CitationRow y JsonCitation del diagrama de clases.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CitationRow:
    """
    Un término a evaluar con su frecuencia.

    Corresponde a CitationRow del diagrama de clases.
    La frecuencia es relevante para estadísticas y ordenamiento
    de resultados, pero no afecta el cálculo de similitud.
    """
    id: str             # Término normalizado (usado como clave)
    citation: str       # Término tal como vino en el JSON de entrada
    frequency: int = 1
    more: dict = field(default_factory=dict)  # Campos adicionales opcionales


@dataclass(slots=True)
class JsonCitation:
    """
    Representación JSON de una cita.
    Corresponde a JsonCitation del diagrama de clases.
    """
    id: str
    citation: str
    more: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {"id": self.id, "citation": self.citation}
        if self.more:
            d.update(self.more)
        return d


def parse_citations(raw: list[dict]) -> list[CitationRow]:
    """
    Convierte el JSON de entrada en CitationRows.

    Formato esperado:
        [{"term": "cap", "frequency": 22593}, ...]

    Acepta también:
        [{"term": "cap"}, ...]          → frequency=1
        ["cap", "patron", ...]          → frequency=1, sin extras
    """
    rows: list[CitationRow] = []
    for item in raw:
        if isinstance(item, str):
            rows.append(CitationRow(id=item, citation=item))
            continue
        term = item.get("term") or item.get("citation") or item.get("id", "")
        freq = int(item.get("frequency", 1))
        more = {k: v for k, v in item.items() if k not in ("term", "citation", "id", "frequency")}
        rows.append(CitationRow(id=term, citation=term, frequency=freq, more=more))
    return rows