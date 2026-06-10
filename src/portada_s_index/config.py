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
    name: str                           # Clave exacta del JSON: "jaro_winkler", etc.
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
    dynamic_min_votes: bool = False     # True => mayoría absoluta de algoritmos ejecutados

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
    algorithm_per_entity: dict[str, list[str]] = field(default_factory=dict)

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
            raw_min_votes = raw_consensus.get("min_votes", 2)
            dynamic_min_votes = (
                isinstance(raw_min_votes, str)
                and raw_min_votes.strip().lower() in {"dynamic", "dinamico", "dinámico", "n/2 + 1", "n/2+1"}
            )
            consensus = ConsensusConfig(
                min_votes=1 if dynamic_min_votes else int(raw_min_votes),
                dynamic_min_votes=dynamic_min_votes,
            )

            algorithms: dict[str, AlgorithmConfig] = {}
            for name, raw in data.get("algorithms", {}).items():
                raw_threshold = raw.get("threshold", 0.7)
                raw_gray_zone = raw.get("gray_zone")
                if isinstance(raw_threshold, (list, tuple)):
                    if len(raw_threshold) != 2:
                        raise ConfigValidationError(
                            f"[{name}] threshold como lista debe ser [threshold, gray_floor]"
                        )
                    threshold = float(raw_threshold[0])
                    gz = (float(raw_threshold[1]), threshold)
                else:
                    threshold = float(raw_threshold)
                    gz_raw = raw_gray_zone if raw_gray_zone is not None else [0.0, 0.0]
                    gz = (float(gz_raw[0]), float(gz_raw[1]))
                algorithms[name] = AlgorithmConfig(
                    name=name,
                    enabled=bool(raw.get("enabled", False)),
                    threshold=threshold,
                    gray_zone=gz,
                    params=dict(raw.get("params", {})),
                )

            algorithm_per_entity: dict[str, list[str]] = {}
            for entity_type, raw_names in data.get("algorithm_per_entity", {}).items():
                if not isinstance(raw_names, list):
                    raise ConfigValidationError(
                        f"algorithm_per_entity.{entity_type} debe ser una lista"
                    )
                names = [str(name) for name in raw_names]
                missing = [name for name in names if name not in algorithms]
                if missing:
                    raise ConfigValidationError(
                        f"algorithm_per_entity.{entity_type} referencia algoritmos no definidos: "
                        f"{', '.join(missing)}"
                    )
                algorithm_per_entity[str(entity_type)] = names

        except (KeyError, TypeError, ValueError) as exc:
            raise ConfigValidationError(f"Error parseando configuración: {exc}") from exc

        return cls(
            version=version,
            normalize=normalize,
            consensus=consensus,
            algorithms=algorithms,
            algorithm_per_entity=algorithm_per_entity,
        )

    # ------------------------------------------------------------------
    # Propiedades
    # ------------------------------------------------------------------

    @property
    def active(self) -> list[AlgorithmConfig]:
        """Solo los algoritmos con enabled=True, en orden de definición."""
        return [a for a in self.algorithms.values() if a.enabled]

    @property
    def execution_algorithms(self) -> list[AlgorithmConfig]:
        """Algoritmos que debe calcular el backend."""
        if self.algorithm_per_entity:
            return list(self.algorithms.values())
        return self.active

    @property
    def active_names(self) -> list[str]:
        return [a.name for a in self.active]

    @property
    def execution_algorithm_names(self) -> list[str]:
        return [a.name for a in self.execution_algorithms]

    def active_for_entity(self, entity_type: str) -> list[AlgorithmConfig]:
        """Algoritmos activos para el tipo de entidad indicado."""
        if not self.algorithm_per_entity:
            return self.active
        if entity_type not in self.algorithm_per_entity:
            raise ConfigValidationError(
                f"algorithm_per_entity no define algoritmos para entity_type={entity_type!r}"
            )
        return [self.algorithms[name] for name in self.algorithm_per_entity[entity_type]]

    def active_names_for_entity(self, entity_type: str) -> list[str]:
        return [a.name for a in self.active_for_entity(entity_type)]

    def allowed_names_for_entity(self, entity_type: str) -> list[str]:
        """Algoritmos que el frontend puede seleccionar para una entidad."""
        if not self.algorithm_per_entity:
            return self.execution_algorithm_names
        if entity_type not in self.algorithm_per_entity:
            raise ConfigValidationError(
                f"algorithm_per_entity no define algoritmos para entity_type={entity_type!r}"
            )
        return list(self.algorithm_per_entity[entity_type])

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
                "min_votes": "dynamic" if self.consensus.dynamic_min_votes else self.consensus.min_votes,
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
            "algorithm_per_entity": self.algorithm_per_entity,
        }
