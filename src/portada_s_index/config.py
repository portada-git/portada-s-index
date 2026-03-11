"""
Configuración del pipeline de desambiguación.

Lee y valida el JSON de configuración del usuario.
Si el JSON tiene errores, falla aquí con mensajes claros,
nunca en mitad del cálculo.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Errores
# ---------------------------------------------------------------------------

class ConfigValidationError(ValueError):
    """El JSON de configuración contiene valores inválidos."""


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class AlgorithmConfig:
    name: str                           # Clave exacta del JSON: "levenshtein_ocr", etc.
    enabled: bool
    threshold: float                    # Umbral de voto positivo [0, 1]
    gray_zone: tuple[float, float]      # (piso, techo) — piso < techo <= threshold
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (0.0 <= self.threshold <= 1.0):
            raise ConfigValidationError(
                f"[{self.name}] threshold={self.threshold} debe estar en [0, 1]"
            )
        piso, techo = self.gray_zone
        if not (0.0 <= piso < techo):
            raise ConfigValidationError(
                f"[{self.name}] gray_zone={self.gray_zone}: piso debe ser < techo"
            )
        if techo > self.threshold:
            raise ConfigValidationError(
                f"[{self.name}] gray_zone techo={techo} supera threshold={self.threshold}"
            )


@dataclass
class ConsensusConfig:
    min_votes: int                      # Mínimo de votos por entidad para CONSENSUS
    require_levenshtein_ocr: bool       # Si True, lev_ocr debe estar entre los votantes

    def __post_init__(self) -> None:
        if self.min_votes < 1:
            raise ConfigValidationError(
                f"consensus.min_votes={self.min_votes} debe ser >= 1"
            )


@dataclass
class PipelineConfig:
    version: int
    normalize: bool
    consensus: ConsensusConfig
    algorithms: dict[str, AlgorithmConfig]  # clave = name del algoritmo

    # ------------------------------------------------------------------
    # Constructores
    # ------------------------------------------------------------------

    @classmethod
    def from_file(cls, path: str | Path) -> "PipelineConfig":
        """Carga y valida desde un archivo JSON."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {p}")
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "PipelineConfig":
        """Construye desde un diccionario (ya parseado desde JSON)."""
        try:
            version = int(data.get("version", 1))
            normalize = bool(data.get("normalize", True))

            raw_consensus = data.get("consensus", {})
            consensus = ConsensusConfig(
                min_votes=int(raw_consensus.get("min_votes", 2)),
                require_levenshtein_ocr=bool(
                    raw_consensus.get("require_levenshtein_ocr", False)
                ),
            )

            algorithms: dict[str, AlgorithmConfig] = {}
            for name, raw in data.get("algorithms", {}).items():
                gz = raw.get("gray_zone", [0.0, 0.0])
                algorithms[name] = AlgorithmConfig(
                    name=name,
                    enabled=bool(raw.get("enabled", False)),
                    threshold=float(raw.get("threshold", 0.7)),
                    gray_zone=(float(gz[0]), float(gz[1])),
                    params=dict(raw.get("params", {})),
                )

        except (KeyError, TypeError, ValueError) as exc:
            raise ConfigValidationError(f"Error parseando configuración: {exc}") from exc

        return cls(
            version=version,
            normalize=normalize,
            consensus=consensus,
            algorithms=algorithms,
        )

    # ------------------------------------------------------------------
    # Propiedades
    # ------------------------------------------------------------------

    @property
    def active(self) -> list[AlgorithmConfig]:
        """Solo los algoritmos con enabled=True, en orden de definición."""
        return [a for a in self.algorithms.values() if a.enabled]

    @property
    def active_names(self) -> list[str]:
        return [a.name for a in self.active]

    def get(self, name: str) -> AlgorithmConfig | None:
        return self.algorithms.get(name)

    # ------------------------------------------------------------------
    # Serialización
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "normalize": self.normalize,
            "consensus": {
                "min_votes": self.consensus.min_votes,
                "require_levenshtein_ocr": self.consensus.require_levenshtein_ocr,
            },
            "algorithms": {
                name: {
                    "enabled": a.enabled,
                    "threshold": a.threshold,
                    "gray_zone": list(a.gray_zone),
                    "params": a.params,
                }
                for name, a in self.algorithms.items()
            },
        }