"""
norms/norm.py — Representación formal de una norma para simulación SNMS.

Una norma en SNMS no es sólo su texto. Es un objeto con:
- Función original (declarada): qué pretendía hacer quien la diseñó
- Función actual (emergente): qué hace realmente tras N rondas
- Índice de deriva funcional (FDI): distancia entre ambas
- Potencial de exaptación: capacidad de adquirir funciones no planeadas
- Registro de spandrels generados

La distinción función_original / función_actual es el corazón teórico
de SNMS, derivada de Gould & Vrba (1982) via la teoría del fenotipo
extendido aplicada al derecho.

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class NormType(Enum):
    """Tipo taxonómico de la norma (nivel jerárquico)."""
    CONSTITUTIONAL = "constitutional"
    STATUTORY = "statutory"
    REGULATORY = "regulatory"
    INFORMAL = "informal"           # Normas informales, costumbres jurídicas
    SYNTHETIC = "synthetic"         # Norma inventada para experimento sandbox


class SelectionLevel(Enum):
    """Nivel en el que opera principalmente la norma."""
    INDIVIDUAL = "L1"       # Afecta principalmente al agente individual
    GROUP = "L2"            # Afecta principalmente a coaliciones/grupos
    POPULATION = "L3"       # Afecta al sistema institucional completo
    MULTILEVEL = "MLV"      # Opera simultáneamente en múltiples niveles


@dataclass
class NormFunction:
    """Descripción de una función normativa (original o actual).

    Attributes:
        label: Etiqueta corta (e.g., "reducción_conflicto_laboral")
        description: Descripción en lenguaje natural
        target_agents: Arquetipos principalmente afectados
        expected_fitness_delta: Cambio de fitness esperado para target_agents [-1,1]
        selection_level: Nivel de selección en que opera
    """
    label: str
    description: str
    target_agents: list[str] = field(default_factory=list)
    expected_fitness_delta: float = 0.0
    selection_level: SelectionLevel = SelectionLevel.MULTILEVEL


@dataclass
class NormativeSpandrel:
    """Efecto secundario de una norma que adquiere función propia.

    En arquitectura: un spandrel es el espacio triangular que resulta
    de colocar un arco sobre pilares cuadrados. En derecho: un efecto
    no planeado de una norma que con el tiempo se vuelve funcionalmente
    autónomo — y puede ser más importante que la norma que lo generó.

    Ejemplo real: La informalidad laboral como spandrel de la legislación
    protectoria excesiva. Surgió como efecto lateral, pero adquirió función
    propia de amortiguador del mercado laboral.
    """
    spandrel_id: str
    origin_norm_id: str             # Norma que generó este spandrel
    emergence_round: int            # Ronda en que fue detectado
    description: str                # Descripción del efecto emergente
    acquired_function: str          # Función autónoma que tomó
    fitness_contribution: float     # Contribución al fitness del sistema [-1,1]
    affected_archetypes: list[str] = field(default_factory=list)
    is_parasitic: bool = False      # True si extrae fitness de L3 hacia L1


@dataclass
class Norm:
    """Norma jurídica completa para simulación SNMS.

    Combina metadata legal con funciones evolutivas y registro de efectos.

    Args:
        norm_id: Identificador único (e.g., "ley_bases_2024", "reforma_laboral_synthetic_01")
        name: Nombre completo de la norma
        norm_type: Tipo taxonómico
        complexity: Complejidad técnica de la norma [0,1]
            Afecta la capacidad de procesamiento de cada arquetipo.
        origin_function: Función declarada (intención del legislador)
        current_function: Función observada (actualizada por el motor tras cada ronda)
        introduction_round: Ronda en que se introduce la norma en la simulación
        text_excerpt: Fragmento representativo del texto normativo (para TribeV2)
        spandrels: Lista de spandrels emergidos de esta norma
        metadata: Datos adicionales (año, fuente, jurisdicción, etc.)
    """
    norm_id: str
    name: str
    norm_type: NormType
    complexity: float
    origin_function: NormFunction
    current_function: Optional[NormFunction] = None     # None hasta ronda > 0
    introduction_round: int = 5
    text_excerpt: str = ""
    spandrels: list[NormativeSpandrel] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        self.complexity = max(0.0, min(1.0, self.complexity))
        if self.current_function is None:
            # Al inicio, la función actual es la declarada
            self.current_function = self.origin_function

    def functional_drift_index(self) -> float:
        """Calcula el Functional Drift Index (FDI).

        Mide qué tan lejos está la función actual de la original.
        Basado en la diferencia de fitness esperado y nivel de selección.

        Returns:
            FDI en [0,1]. 0 = sin deriva. 1 = deriva máxima.
        """
        if self.current_function is None:
            return 0.0

        fitness_drift = abs(
            self.origin_function.expected_fitness_delta
            - self.current_function.expected_fitness_delta
        ) / 2.0  # normalizar a [0,1]

        level_drift = 0.0
        if self.origin_function.selection_level != self.current_function.selection_level:
            level_drift = 0.3  # penalización por cambio de nivel

        return min(1.0, fitness_drift + level_drift)

    def register_spandrel(self, spandrel: NormativeSpandrel) -> None:
        """Registra un nuevo spandrel emergido de esta norma."""
        self.spandrels.append(spandrel)

    def to_dict(self) -> dict:
        """Serializa la norma a diccionario."""
        return {
            "norm_id": self.norm_id,
            "name": self.name,
            "type": self.norm_type.value,
            "complexity": self.complexity,
            "introduction_round": self.introduction_round,
            "origin_function": self.origin_function.label,
            "current_function": self.current_function.label if self.current_function else None,
            "fdi": self.functional_drift_index(),
            "spandrels_count": len(self.spandrels),
        }
